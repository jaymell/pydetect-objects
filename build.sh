#!/bin/bash -xe

. source.sh

TF_MODELS_DIR=${TF_MODELS_DIR:-~/src/tensorflow/models}
MODEL_ARCHIVE=ssd_mobilenet_v1_coco_11_06_2017
MODEL_ARCHIVE_FILE=${MODEL_ARCHIVE}.tar.gz
MODEL_URL=http://download.tensorflow.org/models/object_detection/${MODEL_ARCHIVE_FILE}
MODEL_FILE_NAME=frozen_inference_graph.pb
MODEL_CHECKPOINT_NAME=model.ckpt.data-00000-of-00001

git clone --depth=1 https://github.com/tensorflow/models $LIB_DIR

wget -nv $MODEL_URL -O - | tar xzf - -C /tmp/ && \
  mv /tmp/${MODEL_ARCHIVE}/* ${LIB_DIR}/research/object_detection/

pushd ${LIB_DIR}/research
protoc object_detection/protos/*.proto --python_out=.
popd

