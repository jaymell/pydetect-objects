import boto3
import rx
import time

REGION = 'us-west-2'
STREAM = 'smartcam'

client = boto3.client('kinesis', region_name=REGION)

get_shards = lambda it: it['StreamDescription']['Shards']
get_top_shard = lambda it: get_shards(it)[0]
get_shard_id = lambda it: it['ShardId']
get_shard_iterator = lambda it: it['ShardIterator']
get_records = lambda it: it['Records']

shard_id = get_shard_id(get_top_shard((client.describe_stream(StreamName=STREAM))))

shard_iterator = get_shard_iterator(client.get_shard_iterator(
  StreamName=STREAM,
  ShardId=shard_id,
  ShardIteratorType='LATEST'
))

obs = rx.Observable.from_(get_records(client.get_records(
  ShardIterator = shard_iterator
))).subscribe(lambda it: print('this: %s' % it))

def get_me_records(it):
  try:
    resp = client.get_records(ShardIterator = shard_iterator)
  except Exception as e:
    print('exception: ', dir(e))
    return get_me_records(it)
    time.sleep(.5)
  print(resp)
  return get_me_records(resp['NextShardIterator'])

