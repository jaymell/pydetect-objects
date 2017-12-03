#!/usr/bin/env python3

import logging
import os
import sys
import configparser
from src.detector import tf
from src.source import kinesis
from src.db import dynamo
import rx
from rx.concurrency import ThreadPoolScheduler
import multiprocessing
from rx import config as rx_config
import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

rx_config["concurrency"] = multiprocessing


def load_config():
  CONFIG_FILE = "config"
  p = configparser.ConfigParser()
  p.read(CONFIG_FILE)
  conf = {}
  conf['table'] = os.environ.get('TABLE', p.get('main', 'table'))
  conf['stream'] = os.environ.get('STREAM', p.get('main', 'stream'))
  conf['prob_thresh'] = int(os.environ.get('PROB_THRESH', p.get('main', 'prob_thresh')))
  conf['iterator_type'] = os.environ.get('ITERATOR_TYPE', p.get('main', 'iterator_type'))
  return conf


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
  config = load_config()
  stream = config['stream']
  prob_thresh = config['prob_thresh']
  table = config['table']
  iterator_type = config['iterator_type']

  shard_id = kinesis.get_shard_id(stream)
  source = kinesis.KinesisSource(stream, shard_id, iterator_type)
  detector = tf.TfDetector(prob_thresh=prob_thresh)
  db = dynamo.Dynamo(table)
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
