#!/usr/bin/env python3

import logging
import sys
from src.detector import tf
from src.source import kinesis
import rx
from rx.concurrency import ThreadPoolScheduler
import multiprocessing
from rx import config
import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

config["concurrency"] = multiprocessing

REGION = 'us-west-2'
STREAM = 'smartcam'
BUFFER_TIME = 5000


def print_it(it):
  print('printing: ', it)
  return it


def on_next(it):
  try:
    print("camera id: %s, time: %s, detections: %s" % (it[0].id, it[0].time, it[1]))
  except Exception as e:
    logger.error(e)


def main():
  shard_id = kinesis.get_shard_id(STREAM, REGION)
  source = kinesis.KinesisSource(STREAM, shard_id, REGION)
  detector = tf.TfDetector()
  optimal_thread_count = multiprocessing.cpu_count() + 1
  pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

  def detect_objects(frame, _):
      start = datetime.datetime.now()
      detections = detector.detect_objects(frame.image)
      diff = datetime.datetime.now() - start
      logger.info("Detection time: %s" % diff)
      return (frame, detections)

  def insert_db(frame_detection_pair, _):
    frame = frame_detection_pair[0]
    detections = frame_detection_pair[1]
    if detections:
      print('inserting: ', frame.time, detections)
    return frame_detection_pair

  try:
    rx.Observable.from_iterable(source.get_frames()) \
      .flat_map(lambda it: it) \
      .observe_on(pool_scheduler) \
      .map(detect_objects) \
      .map(insert_db) \
      .subscribe(
        on_next,
        lambda err: logger.error(err),
        lambda it: print('Complete'))
  except Exception as e:
    logger.error("exception: %s" % e)

if __name__ == '__main__':
  main()
