import greengrasssdk  # SDK that exists in the core, not in Cloud
import json
import zlib
import base64
import Connect_Lambda
import time

def handler(event, context):
    decompress_start_time = time.time()
    parsed = json.loads(zlib.decompress(base64.b64decode(event['Message'])))
    decompress_elapsed_time = time.time() - decompress_start_time
    Connect_Lambda.receiveImageBlock(parsed, decompress_elapsed_time)