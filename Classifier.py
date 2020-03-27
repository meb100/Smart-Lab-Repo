import os
from skimage import io, color, transform, img_as_uint
# from skimage.feature import canny
from sklearn import neighbors
import pickle
import math
import numpy


def main():
    TRAINING_DATA_DIRECTORY = "greenDataCollection/TrainingLight"
    TEST_DATA_DIRECTORY = "greenDataCollection/TestLight"
    MODEL_FILE = "trained_model_from_classifier"

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

    # classifier = svm.SVC()
    # classifier = SGDClassifier()
    classifier = neighbors.KNeighborsClassifier()
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
	accuracy = float(correct_count) / float(len(y_correct_vals))
    print("Accuracy = ", accuracy)

def feature_extractor(PARENT_DIRECTORY, X_train, y_train):
    subdirectories = os.listdir(PARENT_DIRECTORY)
    print(subdirectories)
    for subdirectory in subdirectories:
        if subdirectory[0] == '.':
            continue

        print("Loaded subdirectory = ", subdirectory)
        subdirectory_path = os.path.join(PARENT_DIRECTORY, subdirectory)
        walk_output = os.walk(subdirectory_path)
        for dont_care, dont_care_either, all_images in walk_output:
			for image_filename in all_images:
				print("Image = ", image_filename)
				if image_filename[0] == '.':
					continue

				image_raw = io.imread(os.path.join(subdirectory_path, image_filename))
				image_raw = adjust_sizing(image_raw)
				image = convert_to_int(image_raw, True)

				# Create feature vector
				feature_vector = []
				colorsExtractorResult = electrolyticColorsExtractor(image)
				if colorsExtractorResult == -1:
				   continue
				feature_vector.extend(colorsExtractorResult)
				print(feature_vector)
				X_train.append(feature_vector)
				y_train.append(subdirectory)


def colorBins(image):
	BIN_SIZE = 16
	num_bins_one_dim = 256 / BIN_SIZE
	
	bins = [[[0 for b in range(num_bins_one_dim)] for g in range(num_bins_one_dim)] for r in range(num_bins_one_dim)]
	
	for r in range(len(image)):
		for c in range(len(image[0])):
			red_index = image[r][c][0] / BIN_SIZE
			green_index = image[r][c][1] / BIN_SIZE
			blue_index = image[r][c][2] / BIN_SIZE
			bins[red_index][green_index][blue_index] += 1
	
	feature_vector = []
	for r in range(len(bins)):
		for g in range(len(bins[0])):
			for b in range(len(bins[0][0])):
				feature_vector.append(bins[r][g][b])
	
	return feature_vector

def electrolyticColorsExtractor(image):
    # test_image = [[[0.1, 0.1, 0.1] for c in range(len(image[0]))] for r in range(len(image))]
    
    color_counts = [0 for n in range(3)]
    non_background_pixels = 0
    for r in range(len(image)):
        for c in range(len(image[0])):
            if not (backgroundGreenColor(image[r][c]) or backgroundShadowColor(image[r][c])): # background subtraction
                non_background_pixels += 1
                if electrolyticBlueColor(image[r][c]):
                    color_counts[0] += 1
                    # test_image[r][c][1] = 1
                if ceramicColor(image[r][c]):
                    color_counts[1] += 1
                    # test_image[r][c][2] = 1
                if wireColor(image[r][c]):
                    color_counts[2] += 1
                    # test_image[r][c][1] = 1

    # io.imsave("test_image.png", img_as_uint(test_image))
	
    return [float(value)/float(non_background_pixels) for value in color_counts]

def backgroundShadowColor(color):
	return color[0] <= 50 and color[1] <= 50 and color[2] <= 50
	# return abs(color[0] - color[1]) <= 6 and abs(color[1] - color[2]) <= 6 and abs(color[0] - color[2]) <= 6

def backgroundGreenColor(color):
	return color[1] - color[0] > 6 and color[1] - color[0] < 60 and color[1] - color[2] > 40 and color[1] - color[2] <= 120

def electrolyticBlueColor(color):
    return color[2] - color[0] > 6 and color[2] - color[0] < 150

def ceramicColor(color):
    return color[0] - color[1] >= 12 and color[0] - color[1] <= 80 and abs(color[1] - color[2]) < 100

def wireColor(color):
	return color[0] - color[1] > 80 and color[0] - color[1] <= 150 and abs(color[1] - color[2]) < 150

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

    return numpy.mean(min_distances) / numpy.mean(max_distances)


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

def adjust_sizing(image_raw):
    if image_raw.shape[0] < image_raw.shape[1]:
        image_raw = transform.rotate(image_raw, 90, resize=True)
    image_raw = transform.resize(image_raw, (700, 400))
    return image_raw


def convert_to_int(image_raw, decimalRGB):
    image = [[[0, 0, 0] for c in range(len(image_raw[0]))] for r in range(len(image_raw))]
    for r in range(len(image)):
        for c in range(len(image[0])):
			if decimalRGB:
				image[r][c] = [int(image_raw[r][c][0] * 255), int(image_raw[r][c][1] * 255), int(image_raw[r][c][2] * 255)]
			else:
				image[r][c] = [int(image_raw[r][c][0]), int(image_raw[r][c][1]), int(image_raw[r][c][2])]
    return image

if __name__ == '__main__':
    main()
