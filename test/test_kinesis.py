import unittest
import kinesis
import json
from PIL import Image
import os 

class TestKinesis(unittest.TestCase):
  
  def test_get_images(self):
    with open('./run/test/event.js', 'r') as e:
      test_event = json.load(e)
    images = kinesis.get_images(test_event)
    self.assertTrue(list(images[0].getdata()) == list(Image.open('./run/test/lena.jpg').getdata()))
