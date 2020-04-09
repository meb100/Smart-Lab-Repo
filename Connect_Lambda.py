import greengrasssdk
import json
import FeatureExtractor_Lambda
import time


client = greengrasssdk.client('iot-data')

def receiveImageBlock(parsed, decompress_elapsed_time):
    feature_extraction_start_time = 0.0
    feature_extraction_start_time = time.time()
    FeatureExtractor_Lambda.extract_from_block(parsed)
    feature_extraction_elapsed_time = time.time() - feature_extraction_start_time

    msgDict = {"Feature Vector": FeatureExtractor_Lambda.feature_vector_dictionary,
    "DC Time": decompress_elapsed_time, "FV Time": feature_extraction_elapsed_time}
    publish(msgDict)

def publish(messageDictionary):
    jsonString = json.dumps(messageDictionary)
    client.publish(
        topic='component/storage/lambda/to/device/0',
        qos=0,
        payload=jsonString)