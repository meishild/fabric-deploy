# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/8
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================

def create_channel():
    bash = "peer channel create -o orderer.example.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/channel.tx"

