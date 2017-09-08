import unittest
from src.db import dynamo
import datetime
from dateutil import parser
import boto3
from botocore.stub import Stubber

test_put_item = {
  'ResponseMetadata':
  {
    'HTTPHeaders': {
      'connection': 'keep-alive', 'server': 'Server',
      'content-type': 'application/x-amz-json-1.0', 'x-amz-crc32': '2745614147',
      'date': 'Fri, 08 Sep 2017 06:03:58 GMT',
      'x-amzn-requestid': 'sdfsdfsdfsdf',
      'content-length': '2'
    },
    'RequestId': 'asdfasdfasdf',
    'RetryAttempts': 0, 'HTTPStatusCode': 200
  }
}

class TestDynamo(unittest.TestCase):
  def setUp(self):
    self.cli = boto3.client('dynamodb', region_name='us-east-1')
    stubber = Stubber(self.cli)
    stubber.add_response('put_item', test_put_item)
    stubber.activate()
    self.db = dynamo.Dynamo('test_db', 'us-east-1')

  def test_record(self):
    test_id = 1
    test_time = parser.parse('1-1-1980 00:00:00')
    epoch = datetime.datetime.utcfromtimestamp(0)
    test_ms = str((test_time - epoch).total_seconds() * 1000.0)
    test_record = dynamo.DynamoRecord(1, test_time, [('chicken', .75), ('duck', .6 )])

    expected = {
      'camera_id': { 'S':  test_id },
      'time': { 'N': test_ms },
      'detections': { 'L': [ { 'S': 'chicken'}, {'S': 'duck' }]}
    }
    self.assertDictEqual(expected, test_record.record())




# source = kinesis.KinesisSource('teststream', 'test-shard', 'us-east-1')
# images = next(source.get_frames(client))
# self.assertEqual(type(images[0].image), PIL.JpegImagePlugin.JpegImageFile)
# images[0].image.verify()