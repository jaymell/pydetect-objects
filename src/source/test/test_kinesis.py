import unittest
from src.source import kinesis
import json
from PIL import Image
import os

class TestKinesis(unittest.TestCase):

  def test_get_images(self):
    with open('./test/event.js', 'r') as e:
      test_event = json.load(e)
    images = kinesis.get_images(test_event)
    self.assertTrue(list(images[0].getdata()) == list(Image.open('./test/lena.jpg').getdata()))
