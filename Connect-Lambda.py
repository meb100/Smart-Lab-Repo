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

THIS_CORE_NAME = "TODO ADD THIS HERE"
PUBLICATION_TOPIC = ""
SUBSCRIPTION_TOPIC = ""
PICTURE_FILENAME = "receivedImage.jpg"

client = None
receivedMsgCallback = None
imageBlocks = []

def connect(this_core_name, publication_topic, subscription_topic, receivedMsgCallback):
	THIS_CORE_NAME = this_core_name
	PUBLICATION_TOPIC = publication_topic
	SUBSCRIPTION_TOPIC = subscription_topic
	client = greengrasssdk.client(THIS_CORE_NAME)
	client.subscribe(SUBSCRIPTION_TOPIC, 0, messageReceived)

def messageReceived(client, userdata, message):
	if message.topic == SUBSCRIPTION_TOPIC:
		print("Received message with the correct subscription topic. Executing intended action.")
		receivedMsgCallback(message.payload)
	else:
		print("Received message with a different subscription topic. No action taken.")

def receiveImageBlock(message):	
	imageBlocks.append(message)

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

	return pictureFile

def publish(message):
	client.publish(PUBLICATION_TOPIC, message, 0)

	
