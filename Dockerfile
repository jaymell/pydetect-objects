FROM ubuntu:16.04
ENV APP_DIR /app
ENV LIB_DIR $APP_DIR/lib
ENV MODEL_ARCHIVE ssd_mobilenet_v1_coco_11_06_2017
ENV MODEL_ARCHIVE_FILE ${MODEL_ARCHIVE}.tar.gz
ENV MODEL_URL http://download.tensorflow.org/models/object_detection/${MODEL_ARCHIVE_FILE}
ENV MODEL_FILE_NAME frozen_inference_graph.pb
ENV MODEL_CHECKPOINT_NAME model.ckpt.data-00000-of-00001

WORKDIR $APP_DIR

RUN apt-get update && apt-get install -y \
  python3-dev \
  python3-pip \
  python3-setuptools \
  libffi-dev \
  libxml2-dev \
  libxslt1-dev \
  libjpeg8-dev \
  zlib1g-dev \
  libfreetype6-dev \
  liblcms2-dev \
  libwebp-dev \
  git \
  protobuf-compiler \
  wget \
  && rm -rf /var/lib/apt/lists/*

  #tcl8.5-dev tk8.5-dev python-tk
  #libtiff4-dev

COPY requirements.txt $APP_DIR/
RUN pip3 install --no-cache-dir -r requirements.txt

### tensorflow models
###
RUN git clone --depth=1 https://github.com/tensorflow/models $LIB_DIR && \
  bash -O extglob -c 'rm -rf $LIB_DIR/.git* && rm -rf $LIB_DIR/!(research) && rm -rf $LIB_DIR/research/!(slim|object_detection)'

RUN wget -nv $MODEL_URL -O - | tar xzf - -C /tmp/ && \
  mv /tmp/${MODEL_ARCHIVE}/* ${LIB_DIR}/research/object_detection/

WORKDIR $LIB_DIR/research
RUN protoc object_detection/protos/*.proto --python_out=.
WORKDIR $APP_DIR

COPY src $APP_DIR/src
COPY main.py $APP_DIR/
COPY config $APP_DIR/

ENV PYTHONPATH $PYTHONPATH:${LIB_DIR}:${LIB_DIR}/research/slim:${LIB_DIR}/research

CMD [ "python3", "main.py" ]