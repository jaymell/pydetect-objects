#!/bin/bash -xe


TF_MODELS_DIR="/home/james/src/tensorflow/models"
MODEL_ARCHIVE=ssd_mobilenet_v1_coco_11_06_2017
MODEL_ARCHIVE_FILE=${MODEL_ARCHIVE}.tar.gz
MODEL_URL=http://download.tensorflow.org/models/object_detection/${MODEL_ARCHIVE_FILE}
MODEL_FILE_NAME=frozen_inference_graph.pb
MODEL_CHECKPOINT_NAME=model.ckpt.data-00000-of-00001
LIB_DIR="$(pwd)/lib"

rsync -avP  $TF_MODELS_DIR/ ${LIB_DIR}/

[[ -a /tmp/${MODEL_ARCHIVE_FILE} ]] || wget $MODEL_URL -O /tmp/${MODEL_ARCHIVE_FILE}
tar xvf /tmp/${MODEL_ARCHIVE_FILE} -C /tmp/
cp /tmp/${MODEL_ARCHIVE}/* ${LIB_DIR}/object_detection/

pushd ${LIB_DIR}
protoc object_detection/protos/*.proto --python_out=${LIB_DIR}
popd

### source this rather than execute it in order for these variables
### to be available in your current environment

export PYTHONPATH=$PYTHONPATH:${LIB_DIR}:${LIB_DIR}/slim
export LIB_DIR
