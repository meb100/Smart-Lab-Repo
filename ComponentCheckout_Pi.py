'''
n the Raspberry Pi for the Component Checkout.
Code taken and modified from:
https://www.raspberrypi.org/documentation/usage/gpio/python/README.md
https://picamera.readthedocs.io/en/release-1.13/recipes1.html
'''
from PIL import Image
import RPi.GPIO as GPIO
from gpiozero import Button, LED
from time import sleep
from picamera import PiCamera
import Connect_Pi
import json
import pickle
import string
from sklearn import neighbors

LED_1_PIN = 2
LED_2_PIN = 3
LED_3_PIN = 4
BUTTON_PIN = 5
PICTURE_FILENAME = "cameraCapture.jpg"

identifier_to_led = {"Resistor": LED_1_PIN, "Capacitor": LED_2_PIN, "IC": LED_3_PIN}
button = Button(BUTTON_PIN)
camera = PiCamera()

def main():
	Connect_Pi.connect(classifyAndBlinkLED)
	setupCamera()
	# setupGPIO()

	# while True:
	# if GPIO.input(BUTTON_PIN) == 1:
	pictureFile = takePicture()
	Connect_Pi.initiatePublishingImage(pictureFile)
	# msg = {"ComponentName": "Resistor"}
	# Connect_Pi.publish(msg)
	closePictureFile(pictureFile)
	sleep(2)
	
	while True:
		pass	
		
	# GPIO.cleanup()
'''
def setupGPIO():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LED_1_PIN, GPIO.OUT)
	GPIO.setup(LED_2_PIN, GPIO.OUT)
	GPIO.setup(LED_3_PIN, GPIO.OUT)
	GPIO.setup(BUTTON_PIN, GPIO.IN)
'''
def classifyAndBlinkLED(messageDictionary):
	MODEL_FILE = "trained_model"
	
	print("Loaded trained model")
	trained_model_file = open(MODEL_FILE, 'rb')
	classifier = pickle.load(trained_model_file)
	print("Model loaded")
	
	print("Classifying")
	# no_brackets = string.replace(string.replace(messageDictionary["Data"], "[", ""), "]", "")
	# feature_vector = no_brackets.split(", ")
	feature_vector = messageDictionary["Data"]
	result = classifier.predict([feature_vector])
	print("Classification complete. Result: " + result[0])
	
	# GPIO.output([identifier_to_led[result[0]]], GPIO.HIGH)
	# sleep(2)
	# GPIO.output([identifier_to_led[result[0]]], GPIO.LOW)
	# print('Blinked LED corresponding to ' + result[0])

def setupCamera():
	camera.resolution = (400, 700) # (1024, 768)
	sleep(2)

def takePicture():
	camera.capture(PICTURE_FILENAME)
	# return open(PICTURE_FILENAME, "rb")
	return Image.open(PICTURE_FILENAME)

def closePictureFile(pictureFile):
	pictureFile.close()

if __name__ == "__main__":
	main()
