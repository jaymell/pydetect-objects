import unittest
from .. import tf

class TestTF(unittest.TestCase):
  
  def test_detect_objects(self):
    resp = [{'class': {'id': 1, 'name': 'person'}, 'probability': 0.74974597}]
    self.assertEqal(resp, tf.detect_objects('./run/test/lena.jpg'))
