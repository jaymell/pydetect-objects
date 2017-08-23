#!/bin/bash

LIB_DIR=${LIB_DIR:-./lib}
PIPELINE_CONFIG_PATH=./src/ssd_mobilenet_v1.config
CHECKPOINT_PREFIX=${LIB_DIR}/object_detection/model.ckpt

. build.sh

python3 ${LIB_DIR}/object_detection/export_inference_graph.py \
    --input_type encoded_image_string_tensor \
    --pipeline_config_path ${PIPELINE_CONFIG_PATH} \
    --trained_checkpoint_prefix ${CHECKPOINT_PREFIX} \
    --output_directory ./export
