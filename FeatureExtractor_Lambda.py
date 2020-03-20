import pickle

def get_feature_vector(image_blocks):
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

    return feature_vector

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
    # test_image = [[[0.1, 0.1, 0.1] for c in range(len(image[0]))] for r in range(len(image))]
    
    color_counts = [0 for n in range(3)]
    non_background_pixels = 0
    for r in range(len(image)):
        for c in range(len(image[0])):
            if not backgroundGreenColor(image[r][c]): # background subtraction
                non_background_pixels += 1
                if electrolyticBlackColor(image[r][c]):
                    color_counts[0] += 1
                if ceramicColor(image[r][c]):
                    color_counts[1] += 1
                if resistorTan(image[r][c]):
                    color_counts[2] += 1

    # io.imsave("test_image.png", img_as_uint(test_image))
    
    return [float(value)/float(non_background_pixels) for value in color_counts]

def backgroundGreenColor(color):
    return abs(color[0] - color[1]) < 25 and abs(color[1] - color[2]) < 25 and color[0] > 50 and color[1] > 50 and color[2] > 50

def electrolyticBlackColor(color):
    return abs(color[0] - color[1]) < 15 and abs(color[1] - color[2]) < 15 and color[0] < 50 and color[1] < 50 and color[2] < 50

def ceramicColor(color):
    return color[0] - color[1] > 25 and color[0] - color[1] < 70 and abs(color[1] - color[2]) < 15 and color[0] < 100

def resistorTan(color):
    return color[0] - color[1] > 25 and color[0] - color[1] < 60 and abs(color[1] - color[2]) < 15 and color[0] > 100

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