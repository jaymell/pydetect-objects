#!/bin/bash

export PYTHONPATH=$PYTHONPATH:`pwd`/src

. build.sh
python3 -m unittest test/*.py
