import greengrasssdk
import json
import FeatureExtractor_Lambda
import time

numBlocks = -1
blocksProcessed = 0
imageBlocks = []
feature_extraction_start_time = 0.0
client = greengrasssdk.client('iot-data')

def receiveImageBlock(messageDictionary):
    global numBlocks
    global imageBlocks
    global blocksProcessed
    global feature_extraction_start_time

    if messageDictionary["Description"] == "Num Blocks":   # TODO could do all this at end of previous cycle
        print("In Num Blocks block")
        setup_start_time = time.time()
        blocksProcessed = 0
        numBlocks = int(messageDictionary["Data"])
        FeatureExtractor_Lambda.feature_vector = [0, 0, 0]
        FeatureExtractor_Lambda.non_background_pixels = 0
        setup_end_time = time.time()
        setup_elapsed_time = setup_end_time - setup_start_time
        publish({"Description": "Num Blocks Ack", "Time": str(setup_elapsed_time)})
    else:
        blocksProcessed += 1
        if blocksProcessed == 1:
            feature_extraction_start_time = time.time()
        FeatureExtractor_Lambda.extract_from_block(messageDictionary["Data"])
        print("Block number ", int(messageDictionary["Description"]))
        print("Feature vector after update:")
        print(FeatureExtractor_Lambda.feature_vector)
        if blocksProcessed == numBlocks:
            FeatureExtractor_Lambda.normalize_feature_vector()
            feature_extraction_elapsed_time = time.time() - feature_extraction_start_time
            msgDict = {"Description": "Feature Vector", "Data": FeatureExtractor_Lambda.feature_vector, "Time": str(feature_extraction_elapsed_time)}
            publish(msgDict)

def publish(messageDictionary):
    jsonString = json.dumps(messageDictionary)
    print("Publishing: " + jsonString)
    client.publish(
        topic='component/storage/lambda/to/device',
        qos=0,
        payload=jsonString)