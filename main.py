#!/usr/bin/env python3

from src.detector import tf
from src.source import kinesis
import rx

REGION = 'us-west-2'
STREAM = 'smartcam'
BUFFER_COUNT = 2

def main():
  shard_id = kinesis.get_shard_id(STREAM, REGION)
  source = kinesis.KinesisSource(STREAM, shard_id, REGION)
  detector = tf.TfDetector()

  rx.Observable.from_iterable(iter(source.get_images())) \
    .flat_map(lambda it: it) \
    .buffer_with_count(BUFFER_COUNT) \
    .map(lambda images: detector.detect_objects(images)) \
    .subscribe(lambda it: print(it))


if __name__ == '__main__':
  main()

