import pickle

def classify(image_blocks):
    MODEL_FILE = "trained_model"
    BUCKET = "wine-example"

    print("Initializing feature extractor")
    feature_vector = feature_extractor(image_blocks)
    print("Feature extraction complete")
    print("X test data:")
    print(feature_vector)

    if feature_vector is None:
        print("Alert - no X_test data found")
        return "Error"

    # Load trained model
    print("Loading trained model")
    trained_model_file = open(MODEL_FILE, 'rb')
    classifier = pickle.load(trained_model_file)
    print("Model loaded")

    print("Classifying")
    y_test_result = classifier.predict([feature_vector])
    print("Classification complete")

    print("Y output from classifier:")
    print(y_test_result[0])

    return y_test_result[0]

def feature_extractor(image_blocks):
    image = blocks_to_int_image(image_blocks)

    # Create feature vector
    feature_vector = []
    colorsExtractorResult = electrolyticColorsExtractor(image)
    if colorsExtractorResult == -1:
        return
    feature_vector.extend(colorsExtractorResult)
    return feature_vector


def electrolyticColorsExtractor(image):
    color_counts = [0 for n in range(6)]
    non_background_pixels = 0
    for r in range(len(image)):
        for c in range(len(image[0])):
            if not backgroundBrownColor(image[r][c]):  # quick background subtraction
                non_background_pixels += 1
                if electrolyticTextColor(image[r][c]):
                    color_counts[0] += 1
                if electrolyticBlackColor(image[r][c]):
                    color_counts[1] += 1
                if ceramicColor(image[r][c]):
                    color_counts[2] += 1
                if resistorTan(image[r][c]):
                    color_counts[3] += 1
                if resistorBlue(image[r][c]):
                    color_counts[4] += 1
                if resistorGrey(image[r][c]):
                    color_counts[5] += 1
    differences = []
    for other_index in range(2, 6):
        differences.append((color_counts[0] + color_counts[1]) - color_counts[other_index])

    # Normalize differences
    for n in range(len(differences)):
        differences[n] = differences[n] / non_background_pixels

    return [difference / 10000 for difference in differences]

def backgroundBrownColor(color):
    return color[0] - color[1] > 50 and color[0] - color[1] < 80 and color[1] - color[2] > 25 and color[1] - color[2] < 70

def electrolyticTextColor(color):
    return color[0] > 90 and color[1] > 90 and color[2] > 90 and max(color[0], color[1], color[2]) - min(color[0], color[1], color[2]) < 25

def electrolyticBlackColor(color):
    return color[0] < 125 and color[1] < 125 and color[2] < 125 and max(color[0], color[1], color[2]) - min(color[0], color[1], color[2]) < 30

def ceramicColor(color):
    return color[0] - color[1] >= 65 and color[0] - color[1] <= 100 and color[1] - color[2] >= 30

def resistorTan(color):
    return color[0] - color[1] >= 25 and color[0] - color[1] <= 60 and color[1] - color[2] >= 25 and color[1] - color[2] <= 60

def resistorBlue(color):
    return color[0] - color[1] >= 80 and color[0] - color[1] <= 120 and color[1] - color[2] >= 80 and color[1] - color[2] <= 120

def resistorGrey(color):
    return color[0] - color[1] >= 10 and color[0] - color[1] <= 55 and color[1] - color[2] >= 0 and color[1] - color[2] <= 35

# Input: "1,2,3/1,2,3/1,2,3"
# Input: [{"Data": "1,2,3/1,2,3/1,2,3", "Description": 23}, ..., ...] - each block is a row
def blocks_to_int_image(image_blocks):
    image = []
    for block in image_blocks:
        intermed_vector = block["Data"].split("/")  # ["1,2,3", "1,2,3", "1,2,3"]
        row_vector = [entry.split(",") for entry in intermed_vector] # [["1", "2", "3"], ["1", "2", "3"]]
        for c in range(len(row_vector)):
            row_vector[c] = [int(row_vector[c][0]), int(row_vector[c][1]), int(row_vector[c][2])]
        image.append(row_vector)
    return image