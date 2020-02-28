'''
n the Raspberry Pi for the Component Checkout.
Code taken and modified from:
https://www.raspberrypi.org/documentation/usage/gpio/python/README.md
https://picamera.readthedocs.io/en/release-1.13/recipes1.html
'''
import RPi.GPIO as GPIO
from gpiozero import Button, LED
from time import sleep
from picamera import PiCamera
import Connect_Pi
import json

LED_1_PIN = 2
LED_2_PIN = 3
LED_3_PIN = 4
BUTTON_PIN = 5
PICTURE_FILENAME = "cameraCapture.jpg"

identifier_to_led = {"Resistor": LED_1_PIN, "Capacitor": LED_2_PIN, "IC": LED_3_PIN}
button = Button(BUTTON_PIN)
camera = PiCamera()

def main():
	Connect_Pi.connect(blinkLED)
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
def blinkLED(messageDictionary):
	pass
	# GPIO.output([identifier_to_led[messageDictionary["ComponentName"]]], GPIO.HIGH)
	# sleep(2)
	# GPIO.output([identifier_to_led[messageDictionary["ComponentName"]]], GPIO.LOW)
	# print('Blinked LED corresponding to ' + messageDictionary["ComponentName"])

def setupCamera():
	camera.resolution = (1024, 768)
	sleep(2)

def takePicture():
	camera.capture(PICTURE_FILENAME)
	return open(PICTURE_FILENAME, "rb")

def closePictureFile(pictureFile):
	pictureFile.close()

if __name__ == "__main__":
	main()
