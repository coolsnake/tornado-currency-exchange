#!/bin/bash

apt-get update
apt-get install python3-pip -y
pip3 install -r /vagrant/requirements.txt
python3 /vagrant/main.py --port=8888