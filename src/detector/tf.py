#!/usr/bin/python3

import logging
import tensorflow as tf
from object_detection.utils import label_map_util
from PIL import Image
import numpy as np
import datetime
import io
import os
from .interface import ObjectDetector
import threading

logger = logging.getLogger(__name__)

LIB_DIR=os.getenv("LIB_DIR", "lib")
MODEL = os.path.join(LIB_DIR, "research/object_detection/frozen_inference_graph.pb")
PATH_TO_LABELS = os.path.join(LIB_DIR, "research/object_detection/data/mscoco_label_map.pbtxt")

PROB_THRESH = 0.5
NUM_CLASSES = 100


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


class TfDetector(ObjectDetector):

  def __init__(self, model=MODEL, labels=PATH_TO_LABELS, prob_thresh=PROB_THRESH):
    self.lock = threading.Lock()
    self.model = model
    self.label_map = labels
    self.graph = tf.Graph()
    self.session = tf.Session(graph=self.graph)
    self.prob_thresh = prob_thresh

    with self.graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(self.model, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map,
      max_num_classes=NUM_CLASSES, use_display_name=True)
    self.category_index = label_map_util.create_category_index(categories)

  def __del__(self):
    self.session.close()

  def detect_objects(self, image):
    logger.debug('getting lock')
    with self.lock:
      logger.debug('got lock')
      x = tf.placeholder(tf.float32, shape=[None, None, None, 3])

      image_np = load_image_into_numpy_array(image)
      image_np_expanded = np.expand_dims(image_np, axis=0)

      image_tensor = self.graph.get_tensor_by_name('image_tensor:0')
      boxes = self.graph.get_tensor_by_name('detection_boxes:0')
      scores = self.graph.get_tensor_by_name('detection_scores:0')
      classes = self.graph.get_tensor_by_name('detection_classes:0')

      (boxes, scores, classes) = self.session.run(
        [boxes, scores, classes],
        feed_dict={image_tensor: image_np_expanded})

      scores = np.ndarray.flatten(scores)
      classes = np.ndarray.flatten(classes)
      detections = []
      for score, cls in zip(scores, classes):
        # this assumes these are sorted, which is currently
        # the case:
        if score < self.prob_thresh: break
        detections.append( (self.category_index[cls]['name'], score) )
      logger.debug('finished detect_objects. returning')
      return detections
