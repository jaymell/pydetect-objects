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


def on_err(it):
  logger.error(it)
  raise it


def timer(func):
  def wrapped(*args, **kwargs):
    start = datetime.datetime.now()
    resp = func(*args, **kwargs)
    diff = datetime.datetime.now() - start
    logger.info("%s: %s" % (func.__name__, diff))
    return resp
  return wrapped


def get_frames(source):
  return source.get_frames()


@timer
def detect_objects(detector, frame):
  detections = detector.detect_objects(frame.image)
  return (frame, detections)


@timer
def insert_db(Record, db, frame_detection_pair):
  frame = frame_detection_pair[0]
  detections = frame_detection_pair[1]
  print('inserting: ', frame.time, detections)
  record = Record(frame.id, frame.time, detections)
  resp = db.put_record(record)
  return frame_detection_pair


def main():
  shard_id = kinesis.get_shard_id(STREAM, REGION)
  source = kinesis.KinesisSource(STREAM, shard_id, REGION)
  detector = tf.TfDetector()
  db = dynamo.Dynamo(TABLE, REGION)
  Record = dynamo.DynamoRecord
  optimal_thread_count = multiprocessing.cpu_count() + 1
  pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

  try:
    rx.Observable.from_iterable(get_frames(source)) \
      .flat_map(lambda it: it) \
      .flat_map(lambda it: rx.Observable.start(lambda: detect_objects(detector, it))) \
      .filter(lambda frame_detection_pair: len(frame_detection_pair[1]) > 0) \
      .flat_map(lambda frame_detection_pair, _: rx.Observable.start(lambda: insert_db(Record, db, frame_detection_pair))) \
      .subscribe(
        on_next,
        on_err,
        lambda: print('Complete'))
  except Exception as e:
    logger.error("exception: %s" % e)


if __name__ == '__main__':
  main()
