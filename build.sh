#!/bin/bash -xe

TF_MODELS_DIR="/home/james/src/tensorflow/models"
MODEL_ARCHIVE=ssd_mobilenet_v1_coco_11_06_2017
MODEL_ARCHIVE_FILE=${MODEL_ARCHIVE}.tar.gz
MODEL_URL=http://download.tensorflow.org/models/object_detection/${MODEL_ARCHIVE_FILE}
MODEL_FILE_NAME=frozen_inference_graph.pb
MODEL_CHECKPOINT_NAME=model.ckpt.data-00000-of-00001

[[ -a /tmp/${MODEL_ARCHIVE_FILE} ]] || wget $MODEL_URL -O /tmp/${MODEL_ARCHIVE_FILE}

tar xvf /tmp/${MODEL_ARCHIVE_FILE} -C /tmp/
mkdir -p ./run/object_detection
#cp /tmp/${MODEL_ARCHIVE}/${MODEL_FILE_NAME} ./run/object_detection/
#cp /tmp/${MODEL_ARCHIVE}/${MODEL_CHECKPOINT_NAME} ./run/object_detection/
cp /tmp/${MODEL_ARCHIVE}/* ./run/object_detection/

###
### compile protobuff stuff
###

#rsync -avP  $TF_MODELS_DIR/object_detection/ ./run/object_detection
rsync -avP  $TF_MODELS_DIR/ ./run/
rsync -avP  $TF_MODELS_DIR/object_detection/export_inference_graph.py ./run/
#rsync -avP  $TF_MODELS_DIR/slim/ ./run/slim/
rsync -avP src/* ./run/

export PYTHONPATH=$PYTHONPATH:`pwd`/run:`pwd`/run/slim
