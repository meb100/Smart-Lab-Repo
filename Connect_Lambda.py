import greengrasssdk
import json
import FeatureExtractor_Lambda
import time

numBlocks = -1
imageBlocks = []
client = greengrasssdk.client('iot-data')


def receiveImageBlock(messageDictionary):
    global numBlocks
    global imageBlocks

    if messageDictionary["Description"] == "Num Blocks":
        print("In Num Blocks block")
        setup_start_time = time.time()
        numBlocks = int(messageDictionary["Data"])
        imageBlocks = []
        for n in range(numBlocks):
            imageBlocks.append(-1)
        setup_end_time = time.time()
        setup_elapsed_time = setup_end_time - setup_start_time
        publish({"Description": "Num Blocks Ack", "Time": str(setup_elapsed_time)})
    elif messageDictionary["Description"] == "Done Sending Data":
        print("In Done Sending Data block")
        # Check for -1s in imageBlocks
        missingBlockIndices = []
        for n in range(numBlocks):
            if imageBlocks[n] == -1:
                missingBlockIndices.append(str(n))
        if len(missingBlockIndices) == 0:
            print("Image blocks before the call:")
            print(imageBlocks)
            assembleReceivedImage()
        else:
            publish({"Description": "Missing Blocks", "Data": ",".join(missingBlockIndices)})
    else:
        imageBlocks[int(messageDictionary["Description"])] = messageDictionary
        print("Blah appended image block ", int(messageDictionary["Description"]))


# print("number = " + str(messageDictionary["Number"]) + " numBlocks = " + str(numBlocks) + ", imageBlocks length = " + str(len(imageBlocks)))


def assembleReceivedImage():
    global numBlocks
    global imageBlocks
    print("Blah Starting assembleReceivedImage()")
    BLOCK_SIZE = 300
    # jpegString = ""
    
    print("Here is the imageBlocks list:")
    print(imageBlocks)

    # for block in imageBlocks:
    #    jpegString += block["Data"]

    # print("jpegString:" + jpegString)
    
    start_time = time.time()
    result = FeatureExtractor_Lambda.get_feature_vector(imageBlocks)
    end_time = time.time()
    elapsed_time = end_time - start_time

    msgDict = {"Description": "Feature Vector", "Data": result, "Time": str(elapsed_time)}
    publish(msgDict)


def publish(messageDictionary):
    jsonString = json.dumps(messageDictionary)
    print("Publishing: " + jsonString)
    client.publish(
        topic='component/storage/lambda/to/device',
        qos=0,
        payload=jsonString)