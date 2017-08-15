import boto3
import base64
from PIL import Image
import io

get_records = lambda it: it['Records']
get_data = lambda it: base64.b64decode(it['kinesis']['data'])
get_image = lambda it: Image.open(io.BytesIO(it))
