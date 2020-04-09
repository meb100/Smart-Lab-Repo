'''
Some code taken/modified from:
https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
https://picamera.readthedocs.io/en/release-1.13/recipes1.html
'''
from PIL import Image
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
import Connect_Pi
import json
import pickle
import string
import time
import numpy
from sklearn import neighbors

LED_1_PIN = 2
LED_2_PIN = 3
LED_3_PIN = 4
BUTTON_OUT_PIN = 5
BUTTON_IN_PIN = 6
PICTURE_FILENAME = "cameraCapture.png"

identifier_to_led = {"Wire": LED_1_PIN, "Ceramic": LED_2_PIN, "Electrolytic": LED_3_PIN}
camera = PiCamera()

completed_blink = True
classifier = None

checking_out_mode = False
checking_in_mode = False

counts = {"Wire": 0, "Ceramic": 0, "Electrolytic": 0}

global_start_time = -1

resolution = (400, 700)  # (width, height)
global_feature_vector = []
BIN_SIZE = 16

def main():
	global completed_blink
	global classifier
	global checking_out_mode
	global checking_in_mode
	global global_feature_vector
	global global_start_time
	
	Connect_Pi.resolution = resolution
	Connect_Pi.connect(classifyAndBlinkLED)
	setupCamera(resolution)
	setupGPIO()
	classifier = loadTrainedModel()
	num_bins_one_dim = 256 / BIN_SIZE
	global_feature_vector = [0 for n in range(num_bins_one_dim * num_bins_one_dim * num_bins_one_dim)]
	print("Feature vector setup complete")
	
	while True:
		if completed_blink and GPIO.input(BUTTON_OUT_PIN) == 1:
			global_start_time = time.time()
			checking_out_mode = True
			completed_blink = False
			takePicture()
			Connect_Pi.publishImageData()
		elif completed_blink and GPIO.input(BUTTON_IN_PIN) == 1:
			global_start_time = time.time()
			checking_in_mode = True
			completed_blink = False
			takePicture()
			Connect_Pi.publishImageData()
		
	GPIO.cleanup()

def setupGPIO():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LED_1_PIN, GPIO.OUT)
	GPIO.setup(LED_2_PIN, GPIO.OUT)
	GPIO.setup(LED_3_PIN, GPIO.OUT)
	GPIO.setup(BUTTON_OUT_PIN, GPIO.IN)
	GPIO.setup(BUTTON_IN_PIN, GPIO.IN)

def loadTrainedModel():
	# Insert trained model name here
	MODEL_FILE = "trained_model_bins_normalized_700_400"
	
	print("Loading trained model")
	trained_model_file = open(MODEL_FILE, 'rb')
	classifier = pickle.load(trained_model_file)
	print("Model loaded")
	return classifier

def classifyAndBlinkLED():
	global classifier
	global global_feature_vector
	
	for message in Connect_Pi.record:
		messageDictionary = json.loads(message.payload)
		my_feature_vector_dictionary = messageDictionary["Feature Vector"]
		for (index, count) in my_feature_vector_dictionary.iteritems():
			global_feature_vector[int(index)] += count
			
	for n in range(len(global_feature_vector)):
		if global_feature_vector[n] != 0:
			global_feature_vector[n] = float(global_feature_vector[n]) / (float(resolution[0] * resolution[1]))
	
	result = classifier.predict([global_feature_vector])
	
	global_end_time = time.time()
	extracting_features_time = numpy.average(messageDictionary["FV Time"])
	
	blinkLED(result, extracting_features_time, global_end_time)
	
def blinkLED(result, extracting_features_time, global_end_time):
	global completed_blink
	global checking_out_mode
	global checking_in_mode
	global counts
	global global_start_time
	global global_feature_vector
	
	print("Extracting features time, not including decompression (average): " + str(extracting_features_time))
	print("Total time: " + str(global_end_time - global_start_time))
	
	for component in identifier_to_led.keys():
		GPIO.output([identifier_to_led[component]], GPIO.LOW)
	
	for n in range(4):
		GPIO.output([identifier_to_led[result[0]]], GPIO.HIGH)
		sleep(0.35)
		GPIO.output([identifier_to_led[result[0]]], GPIO.LOW)
		sleep(0.35)
	print('Blinked LED corresponding to ' + result[0])
	
	if checking_out_mode:
		counts[result[0]] += 1
		print('Checked out a ' + result[0])
	elif checking_in_mode and counts[result[0]] > 0:
		counts[result[0]] -= 1
		print('Checked in a ' + result[0])
		
	for component in counts.keys():
		if counts[component] > 0:
			GPIO.output([identifier_to_led[component]], GPIO.HIGH)
		else:
			GPIO.output([identifier_to_led[component]], GPIO.LOW)
		
	print('The following components are now checked out:')
	print(counts)
	
	checking_out_mode = False
	checking_in_mode = False
	completed_blink = True
	num_bins_one_dim = 256 / BIN_SIZE
	global_feature_vector = [0 for n in range(num_bins_one_dim * num_bins_one_dim * num_bins_one_dim)]
	Connect_Pi.record = []

def setupCamera(resolution):
	camera.resolution = resolution
	sleep(2)

def takePicture():
	camera.capture(PICTURE_FILENAME)

if __name__ == "__main__":
	main()
