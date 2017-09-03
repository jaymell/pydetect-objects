import boto3
import base64
import io
import time
from .interface import Source
import pprint
import json
from dateutil import parser
from .frame import EncodedFrame
from PIL import Image
import logging
# import kcl

logger = logging.getLogger(__name__)

get_shards = lambda it: it['StreamDescription']['Shards']
get_top_shard = lambda it: get_shards(it)[0]
_get_shard_id = lambda it: it['ShardId']
get_shard_iterator = lambda it: it['ShardIterator']
_get_records = lambda it: it['Records']
# get_data = lambda it: base64.b64decode(it['Data'])
get_data = lambda it: it['Data']
get_image = lambda it: Image.open(io.BytesIO(it))


def get_shard_id(stream, region):
  cli = boto3.client('kinesis', region_name=region)
  return _get_shard_id(get_top_shard((cli.describe_stream(StreamName=stream))))


class KinesisSource(Source):

  def __init__(self, stream, shard_id, region, iterator_type='LATEST'):
    self.stream = stream
    self.shard_id = shard_id
    self.iterator_type = iterator_type
    self.region = region

  def _deserialize(self, serialized):
    frame_json = json.loads(serialized.decode('utf-8'))
    img_bytes = io.BytesIO(base64.b64decode(frame_json['image']))
    img = Image.open(img_bytes)
    time = parser.parse(frame_json['time'])
    width = frame_json['width']
    height = frame_json['height']
    camera_id = frame_json['id']
    frame = EncodedFrame(camera_id, img, width, height, time)
    return frame

  def get_frames(self, cli=None):
    ''' cli as optional parameter allows for injecting mock client '''
    if cli is None:
      cli = boto3.client('kinesis', region_name=self.region)
    iterator = get_shard_iterator(cli.get_shard_iterator(
      StreamName = self.stream,
      ShardId = self.shard_id,
      ShardIteratorType = self.iterator_type
    ))
    while iterator is not None:
      try:
        resp = cli.get_records(ShardIterator = iterator)
      except Exception as e:
        logger.error('exception: %s' % e)
        ## FIXME -- use botocore's backoff, which doesn't seem to be applied by default:
        time.sleep(.5)
        continue
      iterator = resp['NextShardIterator'] if resp['NextShardIterator'] else None
      records = _get_records(resp)
      data = map(get_data, records)
      frames = map(self._deserialize, data)
      yield list(frames)


# class KinesisRecordProcessor(kcl.RecordProcessorBase):
#   def __init__(self, record_handler):
#     self.record_handler = record_handler

#   def initialize(self, shard_id):
#     self.shard_id = shard_id

#   def process_records(self, records, checkpointer):
#     self.record_handler(records)
#     checkpointer.checkpoint()

#   def shutdown(self, checkpointer, reason):
#     pass

