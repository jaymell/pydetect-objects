import boto3
import base64
from PIL import Image
import io
import kcl

get_records = lambda it: it['Records']
get_data = lambda it: base64.b64decode(it['kinesis']['data'])
get_image = lambda it: Image.open(io.BytesIO(it))

def get_images(event):
  records = get_records(event)
  data = map(get_data, records)
  images = map(get_image, data)
  return list(images)


class KinesisRecordProcessor(kcl.RecordProcessorBase):
  def __init__(self, record_handler):
    self.record_handler = record_handler

  def initialize(self, shard_id):
    self.shard_id = shard_id

  def process_records(self, records, checkpointer):
    self.record_handler(records)
    checkpointer.checkpoint()

  def shutdown(self, checkpointer, reason):
    pass

