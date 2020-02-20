'''
Calls functionality from the Greengrass Core SDK on the Greengrass Core
to connect to a Raspberry Pi. Called from within a Lambda and meant to
be reused.

Code taken and modified from:
aws-greengrass-core-sdk-python/examples/greengrassHelloWorldCounter.py
at https://github.com/aws/aws-greengrass-core-sdk-python
'''

import json
import sys

THIS_CORE_NAME = "TODO ADD THIS HERE"
PUBLICATION_TOPIC = ""
SUBSCRIPTION_TOPIC = ""

client = None
receivedMsgCallback = None

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

# This should be the receivedMsgCallback in the image receival case
def receiveImage(message):	
	BLOCK_SIZE = 300

	# TODO. Remember: Image blocks received out of order. Plan: Received them all into a variable,
	# Then after everything received, reconstruct the image and save it to a file.
	


def publish(message):
	client.publish(PUBLICATION_TOPIC, message, 0)

	
