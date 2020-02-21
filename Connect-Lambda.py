'''
Calls functionality from the Greengrass Core SDK on the Greengrass Core
to connect to a Raspberry Pi. Called from within a Lambda and meant to
be reused.

Code taken and modified from:
aws-greengrass-core-sdk-python/examples/greengrassHelloWorldCounter.py
at https://github.com/aws/aws-greengrass-core-sdk-python
'''

import base64
import json
import sys

import greengrasssdk

THIS_CORE_NAME = "TODO ADD THIS HERE"
PUBLICATION_TOPIC = ""
SUBSCRIPTION_TOPIC = ""
PICTURE_FILENAME = "receivedImage.jpg"

client = None
assembledImageCallback = None
imageBlocks = []
numBlocks = -1

def connect(this_core_name, publication_topic, subscription_topic, assembledImageCallback):
	THIS_CORE_NAME = this_core_name
	PUBLICATION_TOPIC = publication_topic
	SUBSCRIPTION_TOPIC = subscription_topic
	client = greengrasssdk.client(THIS_CORE_NAME)
	# client.subscribe(SUBSCRIPTION_TOPIC, 0, messageReceived)

'''
def messageReceived(client, userdata, message):
	if message.topic == SUBSCRIPTION_TOPIC:
		print("Received message with the correct subscription topic. Executing intended action.")
		receivedMsgCallback(message.payload)
	else:
		print("Received message with a different subscription topic. No action taken.")
'''

def receiveImageBlock(event):	
	if event.topic == SUBSCRIPTION_TOPIC:
		print("Message received with subscription topic. Appropriate action will be taken.")
		if event.payload.message["Number"] == "Num Blocks":
			numBlocks = event.payload.message["Data"]
		else:
			imageBlocks.append(event.payload)

		if len(imageBlocks) == numBlocks:
			Connect-Lambda.assembleReceivedImage()
	else:
		print("Message received with different topic from subscription topic. No action will be taken.")

def assembleReceivedImage():
	BLOCK_SIZE = 300

	jpegString = ""

	imageBlocks.sort(key=lambda block: block["Number"])
	for block in imageBlocks:
		jpegString += base64.decodeString(block["Data"])

	pictureFile = open(PICTURE_FILENAME, "w")
	pictureFile.write(jpegString)
	pictureFile.close()

	imageBlocks.clear() # Prep for next image
	numBlocks = -1

	assembledImageCallback(pictureFile)

def publish(message):
	client.publish(PUBLICATION_TOPIC, message, 0)

	
