import greengrasssdk  # SDK that exists in the core, not in Cloud
import json
import Connect_Lambda

def handler(event, context):
    print("Receiving: " + json.dumps(event))
    # event is a dictionary with the "Number" and "Data" entries
    Connect_Lambda.receiveImageBlock(event)