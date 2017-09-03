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
    if type(it) == list:
      for i in it:
        print("camera id: %s, time: %s, detections: %s" % (i[0].id, i[0].time, i[1]))
  except Exception as e:
    logger.error(e)

def main():
  shard_id = kinesis.get_shard_id(STREAM, REGION)
  source = kinesis.KinesisSource(STREAM, shard_id, REGION)
  detector = tf.TfDetector()
  optimal_thread_count = multiprocessing.cpu_count()
  pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

  def detect_objects(frames):
    if frames:
      start = datetime.datetime.now()
      detections = detector.detect_objects([i.image for i in frames])
      diff = datetime.datetime.now() - start
      logger.info("Number of images: %s , time: %s" % (len(frames), diff))
      return list(zip(frames, detections))

  def insert_db(frame_detection_pairs, _):
    if type(frame_detection_pairs) == list:
      for pair in frame_detection_pairs:
        frame = pair[0]
        detections = pair[1]
        print('inserting: ', frame.time, detections)

  try:
    rx.Observable.from_iterable(source.get_frames()) \
      .flat_map(lambda it: it) \
      .buffer_with_time(BUFFER_TIME) \
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


