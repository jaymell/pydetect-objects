import boto3
from .interface import DB
from .record import DBRecord


class Dynamo(DB):

  def __init__(self, db):
    self.db = db

  def put_record(self, record, cli=None):
    if not cli:
      cli = boto3.client('dynamodb')
    return cli.put_item(
      TableName=self.db,
      Item=record.record())


class DynamoRecord(DBRecord):

  def __init__(self, camera_id, time, detections):
    self.id = camera_id
    self.time = time
    self.detections = detections

  def record(self):
    return {
      'camera_id': { 'S': self.id },
      'time': { 'N': str(self.time) },
      'detections': { 'L': [ {'S': i[0] } for i in self.detections ] }
    }
