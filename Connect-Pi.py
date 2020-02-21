'''
Calls functionality from the AWSIoTPythonSDK to connect a Raspberry Pi to
a Lambda on the Greengrass core or on the cloud. Can be called from multiple
modules in the SmartLab project, meant to be generic.

Code in this file is taken and modified from:
aws-iot-device-sdk-python/greengrass/basicDiscovery.py at https://github.com/aws/aws-iot-device-sdk-python
http://www.steves-internet-guide.com/send-file-mqtt/
'''
import base64
import json
import os
import uuid
from AWSIoTPythonSDK.MQTTLib import 
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

GG_CORE_IP = "172.28.212.194"
HASH = "81233cf9d9"
THIS_DEVICE_NAME = "Component_Storage_Device"
PUBLICATION_TOPIC = "Component_Checkout_Image"
SUBSCRIPTION_TOPIC = "Component_Checkout_Response"
CONNECTIVITY_TIMEOUT = 10

connectivityInfoList = [] # May contain many (host, port) options that may work on the gg core
groupCAPath = ""

client = None
receivedMsgCallback = None

def connect(gg_core_ip, hash_encoding, this_device_name, publication_topic, subscription_topic, receivedMsgCallback):
	GG_CORE_IP = gg_core_ip
	HASH = hash_encoding
	THIS_DEVICE_NAME = this_device_name
	PUBLICATION_TOPIC = publication_topic
	SUBSCRIPTION_TOPIC = subscription_topic

	discover()
	connectToCore()

def discover():
	discoveryInfoProvider = DiscoveryInfoProvider()
	discoveryInfoProvider.configureEndpoint(GG_CORE_IP)
	discoveryInfoProvider.configureCredentials("root-ca-cert.pem", HASH + ".cert.pem", HASH + ".private.key")
	discoveryInfoProvider.configureTimeout(CONNECTIVITY_TIMEOUT)

	success = False

	try:
		discoveryInfo = discoveryInfoProvider.discover(THIS_DEVICE_NAME)
		groupID = discoveryInfo.getAllCas()[0][0]
		certificateAuthority = discoveryinfo.getAllCas()[0][1]
		connectivityInfoList = discoveryinfo.getAllCores()[0].connectivityInfoList

		# Save the Group CA file
		groupCAPath = "./groupCA/" + groupID + "_CA_" + str(uuid.uuid4()) + ".crt"
		if not os.path.exists("./groupCA/"):
			os.makedirs("./groupCA/")
		groupCAFile = open(groupCAPath, "w")
		groupCAFile.write(certificateAuthority)
		groupCAFile.close()

		success = True

	except (DiscoveryInvalidRequestException, BaseException) as e:
		print("Exception during discovery phase:")
		print(str(type(e)))

	if success:
		print("Discovery successful.")
	else:
		print("Discovery unsuccessful. System will exit.")
		sys.exit(-1)

def connectToCore():
	client = AWSIoTMQTTClient(THIS_DEVICE_NAME)
	client.configureCredentials(groupCAPath, HASH + ".private.key", HASH + ".cert.pem")

	success = False
	for connectivityInfo in connectivityInfoList:
		client.configureEndpoint(connectivityInfo.host, connectivityInfo.port)
		try:
			client.connect()
			success = True
		except BaseException as e:
			print("Exception while connecting to core.")
			print(e)
			break

	if success:
		print("Connection to core successful.")
	else:
		print("Connection to core unsuccessful. System is exiting.")
		sys.exit(-2)

	# Subscribe to receive messages
	client.subscribe(SUBSCRIPTION_TOPIC, 0, messageReceived)

# The message is the category name. This does not do anything with JSON.
def messageReceived(client, userdata, message):
	# TODO: we want message.payload, and we have to extract the right field from the json...or can I just send without json?
	if message.topic == SUBSCRIPTION_TOPIC:
		print("Received message with the correct subscription topic. Executing intended action.")
		receivedMsgCallback(message.payload)
	else:
		print("Received message with a different subscription topic. No action taken.")

def publish(message):
	client.publish(PUBLICATION_TOPIC, message, 0)

def publishImage(imageFile):
	BLOCK_SIZE = 300
	block = imageFile.read(BLOCK_SIZE)
	counter = 0
	while block is not "":
		jsonDict = {"Number": counter, "Data": base64.b64encode(block)}
		publish(json.dumps(jsonDict))
		counter++
	publish({"Number": "Num Blocks", "Data": counter}) #Send the number of blocks

