import unittest
import tf
import numpy as np

class TestTF(unittest.TestCase):

  def test_detect_objects(self):
    resp = [{'class': {'id': 1, 'name': 'person'}, 'probability': np.float32(0.74974597)}]
    self.assertListEqual(resp, next(tf.detect_objects(['./test/lena.jpg'])))
