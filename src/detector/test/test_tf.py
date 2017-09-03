import unittest
from src.detector import tf
import numpy as np
from PIL import Image

class TestTF(unittest.TestCase):

  def test_detect_one_photo(self):
    ### weak test, only checks category match
    od = tf.TfDetector()
    self.assertEqual('person', od.detect_objects([Image.open('./test/lena.jpg')])[0][0][0])

  def test_detect_multiple_photos(self):
    ### weak test, only checks category match
    od = tf.TfDetector()
    for i in iter(od.detect_objects([Image.open('./test/lena.jpg'), Image.open('./test/lena.jpg')])):
      self.assertEqual('person', i[0][0])

  def test_clean_output(self):
    tf_resp1 = [{'class': {'name': 'cup', 'id': 47}, 'probability': 0.80074477}]
    tf_resp2 = [{'class': {'name': 'cup', 'id': 47}, 'probability': 0.57761276},
      {'class': {'name': 'bowl', 'id': 51}, 'probability': 0.52981782}]
    tf_resp3 = []
    cleaned1 = tf.clean_output(tf_resp1)
    self.assertListEqual(cleaned1, [('cup', 0.80074477)])
    cleaned2 = tf.clean_output(tf_resp2)
    self.assertListEqual(cleaned2, [('cup', 0.57761276), ('bowl', 0.52981782)])
    cleaned3 = tf.clean_output(tf_resp3)
    self.assertListEqual(cleaned3, [])

