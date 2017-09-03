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

logger = logging.getLogger(__name__)

LIB_DIR=os.getenv("LIB_DIR", "lib")
MODEL = os.path.join(LIB_DIR, "object_detection/frozen_inference_graph.pb")
PATH_TO_LABELS = os.path.join(LIB_DIR, "object_detection/data/mscoco_label_map.pbtxt")

PROB_THRESH = 0.5
NUM_CLASSES = 100


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


# return tuple of detection class name and probability:
clean_output = lambda it: [ ( i['class']['name'], i['probability'] ) for i in it ]


class TfDetector(ObjectDetector):

  def __init__(self):
    pass

  def detect_objects(self, images):
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map,
      max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(MODEL, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    def _detect_objects(detection_graph, image, sess):
      x = tf.placeholder(tf.float32, shape=[None, None, None, 3])

      image_np = load_image_into_numpy_array(image)
      image_np_expanded = np.expand_dims(image_np, axis=0)

      image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
      boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
      scores = detection_graph.get_tensor_by_name('detection_scores:0')
      classes = detection_graph.get_tensor_by_name('detection_classes:0')
      num_detections = detection_graph.get_tensor_by_name('num_detections:0')

      (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

      scores = np.ndarray.flatten(scores)
      classes = np.ndarray.flatten(classes)
      detections = []
      for score, cls in zip(scores, classes):
        # this assumes these are sorted, which is currently
        # the case:
        if score < PROB_THRESH: break
        detections.append({ "class": category_index[cls],
          "probability": score})
      return detections

    with detection_graph.as_default():
      with tf.Session(graph=detection_graph) as sess:
        results = [ clean_output(_detect_objects(detection_graph, i, sess)) for i in images ]
        return results
