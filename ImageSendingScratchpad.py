
import base64

numBlocks = -1
imageBlocks = []
PICTURE_FILENAME = "dog_received.jpg"

# TODO can try changing AWS settings to send in binary instead of String
# which I think would save bandwidth and decrease latency

def main():
	imageFile = open("dog.jpg")
	publishImage(imageFile)

def publishImage(imageFile):
	BLOCK_SIZE = 300
	block = imageFile.read(BLOCK_SIZE)
	counter = 0
	while block is not "":
		jsonDict = {"Number": counter, "Data": block}
		# publish(json.dumps(jsonDict))
		print("Publishing... ")
		print(jsonDict)
		receiveImageBlock(jsonDict)

		block = imageFile.read(BLOCK_SIZE)
		counter+=1
	jsonDict = {"Number": "Num Blocks", "Data": counter}
	# publish({"Number": "Num Blocks", "Data": counter}) #Send the number of blocks
	print("Publishing... ")
	print(jsonDict)
	receiveImageBlock(jsonDict)

def receiveImageBlock(messageDictionary):
	print("Receiving... ")
	print(messageDictionary)
	global numBlocks
	if messageDictionary["Number"] == "Num Blocks":
		numBlocks = messageDictionary["Data"]
	else:
		imageBlocks.append(messageDictionary)

	if len(imageBlocks) == numBlocks:
		assembleReceivedImage()

def assembleReceivedImage():
	BLOCK_SIZE = 300

	jpegString = ""

	imageBlocks.sort(key=lambda block: block["Number"])
	for block in imageBlocks:
		jpegString += block["Data"]

	pictureFile = open(PICTURE_FILENAME, "w")
	pictureFile.write(jpegString)
	pictureFile.close()

	del imageBlocks[:] # Prep for next image
	numBlocks = -1

	# assembledImageCallback(pictureFile)
	print("Image has been reassembled")

if __name__ == "__main__":
	main()