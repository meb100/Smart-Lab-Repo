import greengrasssdk  # SDK that exists in the core, not in Cloud
import json

def handler(event, context):
    client = greengrasssdk.client('iot-data')
    client.publish(
        topic='component/storage/lambda/to/device',
        qos=0,
        payload=json.dumps(event))
