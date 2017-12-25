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

logger = logging.getLogger(__name__)

rx_config["concurrency"] = multiprocessing


def load_config():
  CONFIG_FILE = "config"
  p = configparser.ConfigParser()
  p.read(CONFIG_FILE)
  conf = {}
  conf['table'] = os.environ.get('TABLE', p.get('main', 'table'))
  conf['log_level'] = os.environ.get('LOG_LEVEL', p.get('main', 'log_level'))
  conf['stream'] = os.environ.get('STREAM', p.get('main', 'stream'))
  conf['prob_thresh'] = float(os.environ.get('PROB_THRESH', p.get('main', 'prob_thresh')))
  conf['iterator_type'] = os.environ.get('ITERATOR_TYPE', p.get('main', 'iterator_type'))
  return conf


def print_it(it, *args, **kwargs):
  print('printing: ', it, *args, **kwargs)
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
  logger.debug('frame time %s, width %s, height %s' % (frame.time, frame.width, frame.height))
  detections = detector.detect_objects(frame.image)
  return (frame, detections)


@timer
def insert_db(Record, db, frame_detection_pair):
  frame = frame_detection_pair[0]
  detections = frame_detection_pair[1]
  logger.debug('inserting: %s, %s' % (frame.time, detections))
  record = Record(frame.id, frame.time, detections)
  resp = db.put_record(record)
  return frame_detection_pair


def main(config):

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
    # FIXME: this will currently block on detect_objects
    # need buffered/pausable implementation: 
    # this will ultimately cause oom error:
    #  .flat_map(lambda it: rx.Observable.start(lambda: detect_objects(detector, it))) \
    rx.Observable.from_iterable(get_frames(source)) \
      .flat_map(lambda it: it) \
      .map(lambda it: detect_objects(detector, it)) \
      .filter(lambda frame_detection_pair: len(frame_detection_pair[1]) > 0) \
      .flat_map(lambda frame_detection_pair, _: rx.Observable.start(lambda: insert_db(Record, db, frame_detection_pair))) \
      .subscribe(
        on_next,
        on_err,
        lambda: print('Complete'))
  except Exception as e:
    logger.error("exception: %s" % e)
    raise e


def load_logging(log_level_str):
  log_level = getattr(logging, log_level_str.upper())
  logging.basicConfig(stream=sys.stdout, level=log_level)


if __name__ == '__main__':
  config = load_config()
  load_logging(config['log_level'])

  ### reduce aws sdk logging:
  logging.getLogger('boto3').setLevel(logging.WARNING)
  logging.getLogger('botocore').setLevel(logging.WARNING)
  logging.getLogger('nose').setLevel(logging.WARNING)

  main(config)
