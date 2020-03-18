import os
from skimage import io, color, transform, img_as_uint
from skimage.feature import canny
from sklearn import svm
import pickle
import math
import statistics


def main():
    TRAINING_DATA_DIRECTORY = "my_data_1"
    TEST_DATA_DIRECTORY = "my_data_2"
    MODEL_FILE = "trained_model"

    train(TRAINING_DATA_DIRECTORY, MODEL_FILE)
    classify(TEST_DATA_DIRECTORY, MODEL_FILE)

def train(PARENT_DIRECTORY, MODEL_FILE):
    X_train = []
    y_train = []

    print("Initializing trainer")
    feature_extractor(PARENT_DIRECTORY, X_train, y_train)
    print("Feature extraction complete")
    print("X training data:")
    for vector in X_train:
        print(vector)
    print("Y training data")
    print(y_train)

    classifier = svm.SVC()
    # classifier = SGDClassifier()
    # classifier = KNeighborsClassifier()
    # classifier = sklearn.naive_bayes.GaussianNB()
    # classifier = sklearn.tree.DecisionTreeClassifier()

    print("Starting training")
    classifier.fit(X_train, y_train)
    print("Finished training")

    print("Saving model")
    output_file = open(MODEL_FILE, 'wb')
    pickle.dump(classifier, output_file, protocol=2)
    output_file.close()
    print("Model saved")


def classify(PARENT_DIRECTORY, MODEL_FILE):
    X_test = []
    y_correct_vals = []

    print("Initializing classifier")
    feature_extractor(PARENT_DIRECTORY, X_test, y_correct_vals)
    print("Feature extraction complete")
    print("X test data:")
    for vector in X_test:
        print(vector)

    # Load trained model
    print("Loading trained model")
    trained_model_file = open(MODEL_FILE, 'rb')
    classifier = pickle.load(trained_model_file)
    print("Model loaded")

    print("Classifying")
    y_test_result = classifier.predict(X_test)
    print("Classification complete")

    print("Y output from classifier:")
    print(y_test_result)
    print("Correct y output")
    print(y_correct_vals)

    checked_answers = []
    for n in range(len(y_test_result)):
        if y_test_result[n].lower() == y_correct_vals[n].lower():
            checked_answers.append(True)
        else:
            checked_answers.append(False)

    correct_count = 0
    for answer in checked_answers:
        if answer:
            correct_count += 1

    print("Accuracy = ", (correct_count / len(y_correct_vals)))

def feature_extractor(PARENT_DIRECTORY, X_train, y_train):
    subdirectories = [subdir.name for subdir in os.scandir(PARENT_DIRECTORY)]
    for subdirectory in subdirectories:
        if subdirectory[0] == '.':
            continue

        print("Loaded subdirectory = ", subdirectory)
        subdirectory_path = os.path.join(PARENT_DIRECTORY, subdirectory)
        for image_filename in [file.name for file in os.scandir(subdirectory_path)]:
            print("Image = ", image_filename)
            if image_filename[0] == '.':
                continue

            image_raw = io.imread(os.path.join(subdirectory_path, image_filename))
            image_raw = adjust_sizing(image_raw)
            image = convert_to_int(image_raw)
            # distances, normalized_distances = calculate_point_distances(image_raw)
            # if distances == -1 and normalized_distances == -1:
            #     continue

            # Create feature vector
            feature_vector = []
            # feature_vector.append(statistics.stdev(normalized_distances))
            # feature_vector.append(closestFurthestRatio(15, distances))
            colorsExtractorResult = electrolyticColorsExtractor(image)
            if colorsExtractorResult == -1:
               continue
            feature_vector.extend(colorsExtractorResult)
            X_train.append(feature_vector)
            y_train.append(subdirectory)


def adjust_sizing(image_raw):
    if image_raw.shape[0] < image_raw.shape[1]:
        image_raw = transform.rotate(image_raw, 90, resize=True)
    image_raw = transform.resize(image_raw, (700, 400))
    return image_raw


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
    # return differences


    # Normalize color_counts[0], [1] and only return those
    # return [color_counts[0] / 10000, color_counts[1] / 10000]


    return [difference / 10000 for difference in differences]
    # return differences

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

def closestFurthestRatio(num_points, distances):
    my_distances = [distance for distance in distances]
    min_distances = []
    max_distances = []
    for n in range(num_points):
        if len(my_distances) > 50:
            minimum = min(my_distances)
            min_distances.append(minimum)
            my_distances.remove(minimum)
            maximum = max(my_distances)
            max_distances.append(maximum)
            my_distances.remove(maximum)

    if len(min_distances) == 0 or len(max_distances) == 0:
        print("Alert - min_distances or max_distances is 0")
        return -1

    return statistics.mean(min_distances) / statistics.mean(max_distances)


def calculate_point_distances(image_raw):
    greyscale_image = color.rgb2gray(image_raw)
    edges_image = canny(greyscale_image, sigma=3)
    border_image = color_border_pixels(edges_image)
    remove_pin_pixels(border_image, edges_image)
    centroid_x, centroid_y = calculate_centroid(border_image)
    if centroid_x == -1 and centroid_y == -1:
        return -1, -1
    distances = calculate_distances(border_image, centroid_x, centroid_y)
    normalized_distances = normalize_distances(distances)
    if normalized_distances == -1:
        return -1, -1
    return distances, normalized_distances


def normalize_distances(distances):
    max_distance = -1
    normalized_distances = []
    for distance in distances:
        max_distance = max(distance, max_distance)
    if max_distance < 1:
        return -1
    for distance in distances:
        normalized_distances.append(distance / max_distance)
    return normalized_distances


def calculate_distances(border_image, centroid_x, centroid_y):
    # Find distances to white points
    distances = []
    for r in range(len(border_image)):
        for c in range(len(border_image[0])):
            if border_image[r][c]:
                distances.append(math.sqrt(math.pow(c - centroid_x, 2) + math.pow(r - centroid_y, 2)))
    return distances


def calculate_centroid(border_image):
    # Find moment by hand
    numerator_x = 0
    numerator_y = 0
    denominator = 0
    for r in range(len(border_image)):
        for c in range(len(border_image[0])):
            if border_image[r][c]:
                numerator_x += (255 * c)
                numerator_y += (255 * r)
                denominator += 255

    if numerator_x == 0 or numerator_y == 0 or denominator == 0:
        print("Alert - no borders found during centroid calculation")
        return -1, -1
    centroid_x = numerator_x / denominator
    centroid_y = numerator_y / denominator
    return centroid_x, centroid_y


def remove_pin_pixels(border_image, edges_image):
    # Pin removal - detect white pixels on edges_image, but write black pixels to border_image
    # L to R
    PIN_REMOVAL_INWARD_PIXELS = 20
    for r in range(len(edges_image)):
        for c in range(len(edges_image[0])):
            if edges_image[r][c] == True:
                for inward_pixel in range(4, PIN_REMOVAL_INWARD_PIXELS):
                    if c + inward_pixel < len(edges_image[0]) and edges_image[r][c + inward_pixel] == True:
                        for my_inward_pixel in range(-3, inward_pixel + 3):
                            if c + my_inward_pixel >= 0 and c + my_inward_pixel < len(edges_image[0]):
                                border_image[r][c + my_inward_pixel] = False
                        break
                break
    # R to L
    for r in range(len(edges_image)):
        for c in range(len(edges_image[0]) - 1, -1, -1):
            if edges_image[r][c] == True:
                for inward_pixel in range(4, PIN_REMOVAL_INWARD_PIXELS):
                    if c + inward_pixel >= 0 and edges_image[r][c - inward_pixel] == True:
                        for my_inward_pixel in range(-3, inward_pixel + 3):
                            if c - my_inward_pixel >= 0 and c - my_inward_pixel < len(edges_image[0]):
                                border_image[r][c - my_inward_pixel] = False
                        break
                break
    # Top to bottom
    for c in range(len(edges_image[0])):
        for r in range(len(edges_image)):
            if edges_image[r][c] == True:
                for inward_pixel in range(4, PIN_REMOVAL_INWARD_PIXELS):
                    if r + inward_pixel < len(edges_image) and edges_image[r + inward_pixel][c] == True:
                        for my_inward_pixel in range(-3, inward_pixel + 3):
                            if r + my_inward_pixel >= 0 and r + my_inward_pixel < len(edges_image):
                                border_image[r + my_inward_pixel][c] = False
                        break
                break
    # Bottom to top
    for c in range(len(edges_image[0])):
        for r in range(len(edges_image) - 1, -1, -1):
            if edges_image[r][c] == True:
                for inward_pixel in range(4, PIN_REMOVAL_INWARD_PIXELS):
                    if r - inward_pixel >= 0 and edges_image[r - inward_pixel][c] == True:
                        for my_inward_pixel in range(-3, inward_pixel + 3):
                            if r - my_inward_pixel >= 0 and r - my_inward_pixel < len(edges_image):
                                border_image[r - my_inward_pixel][c] = False
                        break
                break


def color_border_pixels(edges_image):
    # Color border pixels only
    # L to R
    border_image = [[False for n in range(len(edges_image[0]))] for m in range(len(edges_image))]
    # [[False] * 4] * 4 - The multiplication produces a shallow copy of the list! So this is a list of references to the one same inner list.
    for r in range(len(edges_image)):
        for c in range(len(edges_image[0])):
            if edges_image[r][c] == True:
                border_image[r][c] = True
                break
    # R to L
    for r in range(len(edges_image)):
        for c in range(len(edges_image[0]) - 1, -1, -1):
            if edges_image[r][c] == True:
                border_image[r][c] = True
                break
    # Top to bottom
    for c in range(len(edges_image[0])):
        for r in range(len(edges_image)):
            if edges_image[r][c] == True:
                border_image[r][c] = True
                break
    # Bottom to top
    for c in range(len(edges_image[0])):
        for r in range(len(edges_image) - 1, -1, -1):
            if edges_image[r][c] == True:
                border_image[r][c] = True
                break
    return border_image


def convert_to_int(image_raw):
    image = [[[0, 0, 0] for c in range(len(image_raw[0]))] for r in range(len(image_raw))]
    for r in range(len(image)):
        for c in range(len(image[0])):
            image[r][c] = [int(image_raw[r][c][0] * 255), int(image_raw[r][c][1] * 255), int(image_raw[r][c][2] * 255)]
    return image

if __name__ == '__main__':
    main()