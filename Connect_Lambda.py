import greengrasssdk
import json
import base64

numBlocks = -1
imageBlocks = []
client = greengrasssdk.client('iot-data')

def receiveImageBlock(messageDictionary):
	global numBlocks
	global imageBlocks
	
	if messageDictionary["Description"] == "Num Blocks":
		numBlocks = int(messageDictionary["Data"])
		imageBlocks = []
		for n in range(numBlocks):
			imageBlocks.append(-1)
		publish({"Description": "Num Blocks Ack", "Data": "Does not matter"})
	elif messageDictionary["Description"] == "Done Sending Data":
		# Check for -1s in imageBlocks
		missingBlockIndices = []
		for n in range(numBlocks):
			if imageBlocks[n] == -1:
				missingBlockIndices.append(str(n))
		if len(missingBlockIndices) == 0:
			assembleReceivedImage()
		else:
			publish({"Description": "Missing Blocks", "Data": ",".join(missingBlockIndices)})
	else:
		imageBlocks[int(messageDictionary["Description"])] = messageDictionary

	# print("number = " + str(messageDictionary["Number"]) + " numBlocks = " + str(numBlocks) + ", imageBlocks length = " + str(len(imageBlocks)))
	

def assembleReceivedImage():
	global numBlocks
	print("Starting assembleReceivedImage()")
	BLOCK_SIZE = 300
	jpegString = ""

	for block in imageBlocks:
		jpegString += block["Data"]
    
	print("jpegString:" + jpegString)
	
	# TODO add the SimpleCV code here
	
	msgDict = {"Description": "Component Name", "Data": "Capacitor"}
	publish(msgDict)

def publish(messageDictionary):
	jsonString = json.dumps(messageDictionary)
	# print("Publishing: " + jsonString)
	client.publish(
		topic='component/storage/lambda/to/device',
		qos=0,
		payload=jsonString)
