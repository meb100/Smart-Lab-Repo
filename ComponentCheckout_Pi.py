'''
n the Raspberry Pi for the Component Checkout.
Code taken and modified from:
https://www.raspberrypi.org/documentation/usage/gpio/python/README.md
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
from sklearn import neighbors

LED_1_PIN = 2
LED_2_PIN = 3
LED_3_PIN = 4
BUTTON_OUT_PIN = 5
BUTTON_IN_PIN = 6
PICTURE_FILENAME = "cameraCapture.jpg"

identifier_to_led = {"Resistor": LED_1_PIN, "Ceramic": LED_2_PIN, "Electrolytic": LED_3_PIN}
camera = PiCamera()

completed_blink = True
classifier = None

checking_out_mode = False
checking_in_mode = False

counts = {"Resistor": 0, "Ceramic": 0, "Electrolytic": 0}

times = []

def main():
	global completed_blink
	global classifier
	global checking_out_mode
	global checking_in_mode
	global times
	
	Connect_Pi.connect(classifyAndBlinkLED)
	setupCamera()
	setupGPIO()
	classifier = loadTrainedModel()

	while True:
		if completed_blink and GPIO.input(BUTTON_OUT_PIN) == 1:
			times.append(time.time())
			checking_out_mode = True
			completed_blink = False
			takePicture()
			times.append(time.time())
			Connect_Pi.initiatePublishingImage()
			times.append(time.time())
		elif completed_blink and GPIO.input(BUTTON_IN_PIN) == 1:
			times.append(time.time())
			checking_in_mode = True
			completed_blink = False
			takePicture()
			times.append(time.time())
			Connect_Pi.initiatePublishingImage()
			times.append(time.time())
		
	GPIO.cleanup()

def setupGPIO():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LED_1_PIN, GPIO.OUT)
	GPIO.setup(LED_2_PIN, GPIO.OUT)
	GPIO.setup(LED_3_PIN, GPIO.OUT)
	GPIO.setup(BUTTON_OUT_PIN, GPIO.IN)
	GPIO.setup(BUTTON_IN_PIN, GPIO.IN)

def loadTrainedModel():
	MODEL_FILE = "trained_model"
	
	print("Loading trained model")
	trained_model_file = open(MODEL_FILE, 'rb')
	classifier = pickle.load(trained_model_file)
	print("Model loaded")
	return classifier

def classifyAndBlinkLED(messageDictionary):
	global completed_blink
	global classifier
	global checking_out_mode
	global checking_in_mode
	global counts
	global times
	global preparing_image_time
	
	feature_vector = messageDictionary["Data"]
	extracting_features_time = float(messageDictionary["Time"])
	
	times.append(time.time())
	print("Classifying")
	result = classifier.predict([feature_vector])
	print("Classification complete. Result: " + result[0])
	times.append(time.time())
	
	print("********")
	print("Timing results:")
	print("Taking picture: " + str(times[1] - times[0]))
	print("Splitting image into blocks: " + str(times[2] - times[1]))
	print("Preparing for receiving image (Lambda): " + str(Connect_Pi.preparing_image_time))
	print("Extracting features (Lambda): " + str(extracting_features_time))
	print("Classifying: " + str(times[4] - times[3]))
	print("********")
	print("Network time (sending ready, sending ack, sending image, sending classification) " + str((times[4] - times[0]) - Connect_Pi.preparing_image_time - extracting_features_time))
	print("********")
	print("Total time: " + str(times[4] - times[0]))
	
	times = []
	
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

def setupCamera():
	camera.resolution = (400, 700) # (1024, 768)
	sleep(2)

def takePicture():
	camera.capture(PICTURE_FILENAME)

if __name__ == "__main__":
	main()
