#!/bin/bash

export PYTHONPATH=$PYTHONPATH:`pwd`

. build.sh
python3 -m unittest src/detector/test/*.py src/source/test/*.py
