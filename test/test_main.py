import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import datetime
from dateutil import parser
from src.source import kinesis
import boto3
from botocore.stub import Stubber
from collections import namedtuple
import time
from io import StringIO
from functools import partial
import sys
from imp import reload

import main


def mock_get_frames(source, sleep=2, out=sys.stdout):
  MockFrame = namedtuple('Frame', ['id', 'image', 'time', 'width', 'height'])
  frame = MockFrame(id="1", image="image", time=1, width=1, height=1)
  print('called get_frames', file=out)
  for i in (frame, frame):
    yield list([frame])
    time.sleep(sleep)


def mock_detect_objects(detector, frame, sleep=5, out=sys.stdout):
  print('called detect_objects', file=out)
  time.sleep(sleep)
  return (frame, [('polar bear', .98)])


def mock_insert_db(Record, db, pair, out=sys.stdout):
  print('called insert_db', file=out)
  return pair


def mock_on_next(it, out=sys.stdout):
  print('on_next called', file=out)


class TestMain(unittest.TestCase):

  def test_concurrency_1(self):
    ''' order of results should indicate concurrency '''
    reload(main)
    out = StringIO()
    main.get_frames = partial(mock_get_frames, out=out)
    main.detect_objects = partial(mock_detect_objects, out=out)
    main.insert_db = partial(mock_insert_db, out=out)
    main.on_next = partial(mock_on_next, out=out)
    main.main()
    time.sleep(10)
    resp = out.getvalue().strip()
    expected = """called get_frames\ncalled detect_objects\ncalled detect_objects\ncalled insert_db\non_next called\ncalled insert_db\non_next called"""
    # print('expected: ', expected)
    # print('actual: ', resp)
    self.assertEqual(resp, expected)

  def test_concurrency_2(self):
    ''' timeouts in this test should make results _look_ sequential '''

    reload(main)
    out = StringIO()
    main.get_frames = partial(mock_get_frames, sleep=5, out=out)
    main.detect_objects = partial(mock_detect_objects, sleep=2, out=out)
    main.insert_db = partial(mock_insert_db, out=out)
    main.on_next = partial(mock_on_next, out=out)
    main.main()
    time.sleep(10)
    expected = """called get_frames\ncalled detect_objects\ncalled insert_db\non_next called\ncalled detect_objects\ncalled insert_db\non_next called"""
    resp = out.getvalue().strip()
    # print('expected: ', expected)
    # print('actual: ', resp)
    self.assertEqual(resp, expected)

  def test_detect_objects(self):
    reload(main)
    mock_return = [('monkey', 0.98 ), ('turducken', 0.70)]
    class MockDetector:
      def detect_objects(self, image):
        return mock_return
    detector = MockDetector()
    MockFrame = namedtuple('Frame', ['id', 'image', 'time', 'width', 'height'])
    frame = MockFrame(id="1", image="image", time=1, width=1, height=1)

    resp = main.detect_objects(detector, frame)
    self.assertEqual(resp[0], frame)
    self.assertListEqual(resp[1], mock_return)

  def test_insert_db(self):
    reload(main)
    MockFrame = namedtuple('Frame', ['id', 'image', 'time', 'width', 'height'])
    frame = MockFrame(id="1", image="image", time=1, width=1, height=1)
    mock_detection = [('monkey', 0.98 ), ('turducken', 0.70)]
    mock_return = (frame, mock_detection)

    resp = main.insert_db(MagicMock(), MagicMock(), mock_return)
    self.assertEqual(resp[0], frame)
    self.assertListEqual(resp[1], mock_detection)