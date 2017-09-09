#!/usr/bin/env python3

import logging
import sys
from src.detector import tf
from src.source import kinesis
from src.db import dynamo
import rx
from rx.concurrency import ThreadPoolScheduler
import multiprocessing
from rx import config
import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

config["concurrency"] = multiprocessing

# move to config file:
REGION = 'us-west-2'
STREAM = 'smartcam'
TABLE = 'smartcam'
BUFFER_TIME = 5000


def print_it(it):
  print('printing: ', it)
  return it


def on_next(it):
  try:
    print("camera id: %s, time: %s, lag: %s, detections: %s" % (it[0].id,
      it[0].time, datetime.datetime.utcnow() - it[0].time, it[1]))
  except Exception as e:
    logger.error(e)


def main():
  shard_id = kinesis.get_shard_id(STREAM, REGION)
  source = kinesis.KinesisSource(STREAM, shard_id, REGION)
  detector = tf.TfDetector()
  db = dynamo.Dynamo(TABLE, REGION)
  Record = dynamo.DynamoRecord
  optimal_thread_count = multiprocessing.cpu_count() + 1
  pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

  def detect_objects(frame, _):
    start = datetime.datetime.now()
    detections = detector.detect_objects(frame.image)
    diff = datetime.datetime.now() - start
    logger.info("Detection time: %s" % diff)
    return (frame, detections)

  def insert_db(db, frame_detection_pair):
    frame = frame_detection_pair[0]
    detections = frame_detection_pair[1]
    print('inserting: ', frame.time, detections)
    record = Record(frame.id, frame.time, detections)
    resp = db.put_record(record)
    print('resp: ', resp)
    return frame_detection_pair

  try:
    rx.Observable.from_iterable(source.get_frames()) \
      .flat_map(lambda it: it) \
      .observe_on(pool_scheduler) \
      .map(detect_objects) \
      .filter(lambda frame_detection_pair: len(frame_detection_pair[1]) > 0) \
      .map(lambda frame_detection_pair, _: insert_db(db, frame_detection_pair)) \
      .subscribe(
        on_next,
        lambda err: logger.error(err),
        lambda it: print('Complete'))
  except Exception as e:
    logger.error("exception: %s" % e)


if __name__ == '__main__':
  main()
