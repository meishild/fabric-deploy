# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018-11-28
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import os

from jinja2 import Environment, PackageLoader

path = os.path.dirname(os.path.realpath(__file__))
deploy_path = path + "/deploy/"
machine_path = path + "/machine/"

env = Environment(loader=PackageLoader('templates', 'docker'))
f_env = Environment(loader=PackageLoader('templates', 'fabric'))
b_env = Environment(loader=PackageLoader('templates', 'bash'))

volumes_path = "/opt/chainData"

channel_name = 'mychannel'
default_net = 'net'
