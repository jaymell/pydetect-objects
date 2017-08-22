#!/bin/bash

PIPELINE_CONFIG_PATH=./run/ssd_mobilenet_v1.config
#CHECKPOINT_PATH=./run/object_detection/model.ckpt.data-00000-of-00001
CHECKPOINT_PREFIX=./run/object_detection/model.ckpt

. build.sh

python3 ./run/export_inference_graph.py \
    --input_type encoded_image_string_tensor \
    --pipeline_config_path ${PIPELINE_CONFIG_PATH} \
    --trained_checkpoint_prefix ${CHECKPOINT_PREFIX} \
    --output_directory ./

#python3 ./run/export_inference_graph.py \
#    --input_type encoded_image_string_tensor \
#    --pipeline_config_path ${PIPELINE_CONFIG_PATH} \
#    --checkpoint_path ${CHECKPOINT_PATH} \
#    --trained_checkpoint_prefix ${CHECKPOINT_PREFIX} \
#    --inference_graph_path output_inference_graph.pb \
#    --output_directory ./

