import unittest
from src.detector import tf
import numpy as np

class TestTF(unittest.TestCase):

  def test_detect_one_photo(self):
    resp = [{'class': {'id': 1, 'name': 'person'}, 'probability': np.float32(0.74308306)}]
    od = tf.TfDetector()
    self.assertListEqual(resp, next(od.detect_objects(['./test/lena.jpg'])))

  def test_detect_multiple_photos(self):
    resp = [[{'class': {'id': 1, 'name': 'person'}, 'probability': np.float32(0.74308306)}],
      [{'class': {'id': 1, 'name': 'person'}, 'probability': np.float32(0.74308306)}]]
    od = tf.TfDetector()
    self.assertListEqual(resp, [i for i in iter(od.detect_objects(['./test/lena.jpg',
      './test/lena.jpg']))])
