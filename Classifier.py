import os
from sklearn import neighbors, metrics, svm, linear_model, naive_bayes, tree
import pickle
import math
import numpy
from PIL import Image

def main():
	# Edit the constants in main()
	TRAINING_DATA_DIRECTORY = "dataset/TrainingLight"
	TEST_DATA_DIRECTORY = "dataset/TestLight"
	resolution = (400, 700)
	bin_size = 16
	MODEL_FILE = "trained_model_output_filename"
	
	train(TRAINING_DATA_DIRECTORY, MODEL_FILE, resolution, bin_size)
	classify(TEST_DATA_DIRECTORY, MODEL_FILE, resolution, bin_size)

def train(PARENT_DIRECTORY, MODEL_FILE, resolution, bin_size):
    X_train = []
    y_train = []

    print("Initializing trainer")
    feature_extractor(PARENT_DIRECTORY, X_train, y_train, resolution, bin_size)
    print("Feature extraction complete")

    classifier = neighbors.KNeighborsClassifier()
    # classifier = svm.SVC()
    # classifier = SGDClassifier()
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


def classify(PARENT_DIRECTORY, MODEL_FILE, resolution, bin_size):
    X_test = []
    y_correct_vals = []

    print("Initializing classifier")
    feature_extractor(PARENT_DIRECTORY, X_test, y_correct_vals, resolution, bin_size)
    print("Feature extraction complete")

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
	
    print(metrics.classification_report(y_correct_vals, y_test_result))
	
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

def feature_extractor(PARENT_DIRECTORY, X_train, y_train, resolution, bin_size):
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
				
				imageFile = Image.open(os.path.join(subdirectory_path, image_filename))
				imageFile = imageFile.resize(resolution)
				image = imageFile.load()
				
				# Create feature vector
				feature_vector = []
				colorsExtractorResult = colorBins(imageFile, image, bin_size)  # explicitColorsExtractor(imageFile, image)
				if colorsExtractorResult == -1:
				   continue
				feature_vector.extend(colorsExtractorResult)

				X_train.append(feature_vector)
				y_train.append(subdirectory)


def colorBins(imageFile, image, bin_size):
	BIN_SIZE = bin_size
	num_bins_one_dim = 256 / BIN_SIZE
	
	bins = [[[0 for b in range(num_bins_one_dim)] for g in range(num_bins_one_dim)] for r in range(num_bins_one_dim)]
	
	for r in range(imageFile.size[1]):
		for c in range(imageFile.size[0]):
			red_index = image[c, r][0] / BIN_SIZE
			green_index = image[c, r][1] / BIN_SIZE
			blue_index = image[c, r][2] / BIN_SIZE
			bins[red_index][green_index][blue_index] += 1
	
	feature_vector = []
	for r in range(len(bins)):
		for g in range(len(bins[0])):
			for b in range(len(bins[0][0])):
				feature_vector.append(float(bins[r][g][b]) / float(imageFile.size[0] * imageFile.size[1]))
	
	return feature_vector

def explicitColorsExtractor(imageFile, image):
    color_counts = [0 for n in range(3)]
    non_background_pixels = 0
    for r in range(imageFile.size[1]):
        for c in range(imageFile.size[0]):
            if not (backgroundGreenColor(image[c, r]) or backgroundShadowColor(image[c, r])): # background subtraction
                non_background_pixels += 1
                if electrolyticBlueColor(image[c, r]):
                    color_counts[0] += 1
                if ceramicColor(image[c, r]):
                    color_counts[1] += 1
                if wireColor(image[c, r]):
                    color_counts[2] += 1
	
    return [float(value)/float(non_background_pixels) for value in color_counts]

def backgroundShadowColor(color):
	return color[0] <= 50 and color[1] <= 50 and color[2] <= 50

def backgroundGreenColor(color):
	return color[1] - color[0] > 6 and color[1] - color[0] < 60 and color[1] - color[2] > 40 and color[1] - color[2] <= 120

def electrolyticBlueColor(color):
    return color[2] - color[0] > 6 and color[2] - color[0] < 150

def ceramicColor(color):
    return color[0] - color[1] >= 12 and color[0] - color[1] <= 80 and abs(color[1] - color[2]) < 100

def wireColor(color):
	return color[0] - color[1] > 80 and color[0] - color[1] <= 150 and abs(color[1] - color[2]) < 150

if __name__ == '__main__':
    main()
