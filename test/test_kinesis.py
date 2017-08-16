import unittest
from src import kinesis
import json
from PIL import Image
import os 

class TestKinesis(unittest.TestCase):
  
  def test_get_images(self):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open('test/testevent.js', 'r') as e:
      test_event = json.load(e)
    images = kinesis.get_images(test_event)
    print(dir(self))
    self.assertTrue(list(images[0].getdata()) == list(Image.open('test/test.jpeg').getdata()))
