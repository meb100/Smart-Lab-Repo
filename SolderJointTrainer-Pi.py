'''
Top-level module run on the Raspberry Pi for the Solder Joint Trainer.

Code taken and modified from:
https://www.raspberrypi.org/documentation/usage/gpio/python/README.md
https://picamera.readthedocs.io/en/release-1.13/recipes1.html
'''

from gpiozero import Button
from time import sleep
from picamera import PiCamera
import Connect-Pi

LED_1_PIN = 1
LED_2_PIN = 2
LED_3_PIN = 3
BUTTON_PIN = 4
PICTURE_FILENAME = "cameraCapture.jpg"

identifier_to_led = {"Resistor": LED(LED_1_PIN), "Capacitor": LED(LED_2_PIN), "IC": LED(LED_3_PIN)}
button = Button(BUTTON_PIN)
camera = PiCamera()
pictureFile = open(PICTURE_FILENAME)

def main():
	Connect-Pi.connect(___, ___, ___, ___, ___, blinkLED) # TODO add parameters
	setupCamera()
	while True:
		button.wait_for_press()
		Connect-Pi.publishImage(takePicture())
	closePictureFile()

def blinkLED(componentName):
	identifier_to_led[componentName].on()
	sleep(1)
	identifier_to_led[componentName].off()

def setupCamera():
	camera.resolution = (1024, 768)
	camera.start_preview()
	sleep(2)

def takePicture():
	camera.capture(PICTURE_FILENAME)
	pictureFile = open(PICTURE_FILENAME, "rb")

def closePictureFile():
	pictureFile.close()

if __name__ == "__main__":
	main()