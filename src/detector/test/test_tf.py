import unittest
from src.detector import tf
import numpy as np
from PIL import Image

class TestTF(unittest.TestCase):

  def test_detect_one_photo(self):
    ### weak test, only checks category match
    od = tf.TfDetector()
    self.assertEqual('person', od.detect_objects(Image.open('./test/lena.jpg'))[0][0])
