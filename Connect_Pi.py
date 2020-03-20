# Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License").
# * You may not use this file except in compliance with the License.
# * A copy of the License is located at
# *
# *  http://aws.amazon.com/apache2.0
# *
# * or in the "license" file accompanying this file. This file is distributed
# * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# * express or implied. See the License for the specific language governing
# * permissions and limitations under the License.
# */

from PIL import Image
import string
import base64
import os
import sys
import time
import uuid
import json
import logging
import argparse
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException

AllowedActions = ['both', 'publish', 'subscribe']

MAX_DISCOVERY_RETRIES = 10
GROUP_CA_PATH = "./groupCA/"

# Constants
host = "a2t04pbjeytmzz-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "root-ca-cert.pem"
certificatePath = "81233cf9d9.cert.pem"
privateKeyPath = "81233cf9d9.private.key"
clientId = "Component_Storage_Device"
thingName = "Component_Storage_Device"
publication_topic = "component/storage/device/to/lambda"
subscription_topic = "component/storage/lambda/to/device"

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)

receiveFunction = None
imageBlocks = []

def connect(myReceiveFunction):
    global receiveFunction
    receiveFunction = myReceiveFunction

    if not os.path.isfile(certificatePath):
        parser.error("No certificate found at {}".format(certificatePath))
        exit(3)

    if not os.path.isfile(privateKeyPath):
        parser.error("No private key found at {}".format(privateKeyPath))
        exit(3)

    # Progressive back off core
    backOffCore = ProgressiveBackOffCore()

    # Discover GGCs
    discoveryInfoProvider = DiscoveryInfoProvider()
    discoveryInfoProvider.configureEndpoint(host)
    discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
    discoveryInfoProvider.configureTimeout(10)  # 10 sec

    retryCount = MAX_DISCOVERY_RETRIES 
    discovered = False
    groupCA = None
    coreInfo = None
    while retryCount != 0:
        try:
            discoveryInfo = discoveryInfoProvider.discover(thingName)
            caList = discoveryInfo.getAllCas()
            coreList = discoveryInfo.getAllCores()

            # We only pick the first ca and core info
            groupId, ca = caList[0]
            coreInfo = coreList[0]

            groupCA = GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
            if not os.path.exists(GROUP_CA_PATH):
                os.makedirs(GROUP_CA_PATH)
            groupCAFile = open(groupCA, "w")
            groupCAFile.write(ca)
            groupCAFile.close()

            discovered = True
            break
        except DiscoveryInvalidRequestException as e:
            print("Invalid discovery request detected!")
            print("Type: %s" % str(type(e)))
            print("Error message: %s" % e.message)
            print("Stopping...")
            break
        except BaseException as e:
            print("Error in discovery!")
            print("Type: %s" % str(type(e)))
            print("Error message: %s" % e.message)
            retryCount -= 1
            print("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
            print("Backing off...\n")
            backOffCore.backOff()

    if not discovered:
        print("Discovery failed after %d retries. Exiting...\n" % (MAX_DISCOVERY_RETRIES))
        sys.exit(-1)

    # Iterate through all connection options for the core and use the first successful one
    myAWSIoTMQTTClient.configureCredentials(groupCA, privateKeyPath, certificatePath)
    myAWSIoTMQTTClient.onMessage = customOnMessage

    connected = False
    for connectivityInfo in coreInfo.connectivityInfoList:
        currentHost = connectivityInfo.host
        currentPort = connectivityInfo.port
        myAWSIoTMQTTClient.configureEndpoint(currentHost, currentPort)
        try:
            myAWSIoTMQTTClient.connect()
            connected = True
            break
        except BaseException as e:
            print("Error in connect!")
            print("Type: %s" % str(type(e)))
            print("Error message: %s" % e.message)

    if not connected:
        print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
        sys.exit(-2)

    # Successfully connected to the core
    myAWSIoTMQTTClient.subscribe(subscription_topic, 0, None)
    time.sleep(2)

# General message notification callback
# With current settings on my AWS account, the message payload must be JSON
def customOnMessage(message):
	print('Received message on topic %s: %s\n' % (message.topic, message.payload))
	messageDictionary = json.loads(message.payload)
	if messageDictionary["Description"] == "Num Blocks Ack":
		publishImageData(range(len(imageBlocks)))
	elif messageDictionary["Description"] == "Missing Blocks":
		publishImageData(str.split(str(messageDictionary["Data"]), ","))
	elif messageDictionary["Description"] == "Feature Vector":
		receiveFunction(messageDictionary)
	else:
		print("Received message did not have a recognized Description field")
	
def publish(messageDictionary):
    messageJSON = json.dumps(messageDictionary)
    myAWSIoTMQTTClient.publish(publication_topic, messageJSON, 0)
    print('Published topic %s: %s\n' % (publication_topic, messageJSON))
    time.sleep(1)
    
def publishSingleImage(messageDictionary):
    messageJSON = json.dumps(messageDictionary)
    myAWSIoTMQTTClient.publish(publication_topic, messageJSON, 0)
    # print('Published topic %s: %s\n' % (publication_topic, messageJSON)) 
    
def initiatePublishingImage(imageFile):
	global imageBlocks
	imageBlocks = []

	# Each row sent separately
	fullImage = imageFile.load()
	print(imageFile.size)
	for r in range(imageFile.size[1]):
		row_data_list = []
		for c in range(imageFile.size[0]):
			row_data_list.append(fullImage[c, r])  # c is x coord, r is y coord
		row_data_list_strings = [str(pixel) for pixel in row_data_list]
		row_data_string = "".join(row_data_list_strings)
		row_data_string = string.replace(string.replace(string.replace(string.replace(row_data_string, ", ", ","), ")(", "/"), "(", ""), ")", "")
		jsonDict = {"Description": r, "Data": row_data_string}
		imageBlocks.append(jsonDict)
		
	print(imageBlocks[0])
	jsonDict = {"Description": "Num Blocks", "Data": imageFile.size[1]}
	publish(jsonDict)
	
# whichBlocks is list of indices
counter = 0

def publishImageData(whichBlocks):
	global counter;
	
	for indexStr in whichBlocks:
		index = int(indexStr)
		print("Publishing index: ", index)
		publishSingleImage(imageBlocks[index])		
	counter += 1

	time.sleep(3) # Tune this so it's always after all data is received. On the other hand, seems like
	# Lambda always receives the data (if it receives it at all) in same order as published
	publish({"Description": "Done Sending Data", "Data": "Does not matter"})
	
