'''
Some code (espeically the discovery part) taken and modified from:
https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/greengrass/basicDiscovery.py
'''

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
import zlib
import math
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
publication_topic_0 = "component/storage/device/to/lambda/0"
publication_topic_1 = "component/storage/device/to/lambda/1"
publication_topic_2 = "component/storage/device/to/lambda/2"
publication_topic_3 = "component/storage/device/to/lambda/3"
subscription_topic_0 = "component/storage/lambda/to/device/0"
subscription_topic_1 = "component/storage/lambda/to/device/1"
subscription_topic_2 = "component/storage/lambda/to/device/2"
subscription_topic_3 = "component/storage/lambda/to/device/3"

myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)

# Variables
receiveFunction = None
resolution = (0, 0)
rows_per_block = 14
record = []

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
    myAWSIoTMQTTClient.subscribe(subscription_topic_0, 0, None)
    myAWSIoTMQTTClient.subscribe(subscription_topic_1, 0, None)
    myAWSIoTMQTTClient.subscribe(subscription_topic_2, 0, None)
    myAWSIoTMQTTClient.subscribe(subscription_topic_3, 0, None)
    time.sleep(2)

def customOnMessage(message):
	global record
	global resolution
	global rows_per_block
	
	record.append(message)
	# print('Received message on topic %s: %s\n' % (message.topic, message.payload))
	if len(record) == math.ceil(float(resolution[1]) / float(rows_per_block)):
		receiveFunction()

def publish(messageDictionary, this_publication_topic):
    messageJSON = json.dumps(messageDictionary)
    myAWSIoTMQTTClient.publish(this_publication_topic, messageJSON, 0)
    print('Published topic %s: %s\n' % (this_publication_topic, messageJSON))
    time.sleep(1)
    
def publishSingleImage(formatted_block, this_publication_topic):
    myAWSIoTMQTTClient.publish(this_publication_topic, formatted_block, 0) 

def publishImageData():
	global rows_per_block
	
	# PIL is much faster than io.imread in sklearn
	imageFile = Image.open("cameraCapture.png")
	fullImage = imageFile.load()
	
	print(imageFile.size)
	
	block = []
	publication_topic_number = 0
	for r in range(imageFile.size[1]):  # imageFile.size: (width, height)
		row_data_list = []
		for c in range(imageFile.size[0]):
			fullImage_list = [fullImage[c, r][0], fullImage[c, r][1], fullImage[c, r][2]]  # Must be list for loads parsing in Lambda
			row_data_list.append(fullImage_list)  # c is x coord, r is y coord
		block.append(row_data_list)
		if r % rows_per_block == rows_per_block - 1:
			compressedMessage = base64.b64encode(str(block).encode('zlib_codec'))
			publishSingleImage(json.dumps({"Message": compressedMessage}), "component/storage/device/to/lambda/" + str(publication_topic_number))
			# Uncomment for 4 Lambdas
			# publication_topic_number = (publication_topic_number + 1) % 4			
			block = []
			
	if resolution[1] % rows_per_block != 0:
		compressedMessage = base64.b64encode(str(block).encode('zlib_codec'))
		publishSingleImage(json.dumps({"Message": compressedMessage}), "component/storage/device/to/lambda/" + str(publication_topic_number))
		
	imageFile.close()
	


	
