import boto3
from .interface import DB

client = boto3.client('dynamodb')

class Dynamo(DB):

  def __init__(self, db):
    self.db = db

  def put_record(self, record):
    pass


class Record:
  pass
