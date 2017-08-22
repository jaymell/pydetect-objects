sudo yum install -y gcc zlib zlib-devel openssl openssl-devel
sudo yum install protobuf-compiler 
sudo yum install git

wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar -xzvf Python-3.6.1.tgz

cd Python-3.6.1 && ./configure && make

sudo make install

sudo /usr/local/bin/pip3 install virtualenv

/usr/local/bin/virtualenv ~/shrink_venv

source ~/shrink_venv/bin/activate

pip install Pillow

pip install lxml

pip install tensorflow

cd ~

git clone https://github.com/tensorflow/models

. build.sh

cd $VIRTUAL_ENV/lib/python3.6/site-packages

zip -r9 ~/CreateThumbnail.zip *

cd ~/pydetect-objects

zip -g CreateThumbnail.zip


