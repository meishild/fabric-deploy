# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/14
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
volumes_path = "/opt/chainData"

orderer_tmpl_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'shuwen.com',
    'ips': ['192.168.12.74', '192.168.12.75'],
    'ports': [7050],
    'type': 'kafka',
    'zookeeper': {
        'ips': ['192.168.12.74', '192.168.12.75', '192.168.12.76'],
        'ports': [2181, 2888, 3888]
    },
    'kafka': {
        'ips': ['192.168.12.74', '192.168.12.75', '192.168.12.76', '192.168.12.77'],
        'ports': [9092]
    },
}

peer_tmpl_list = [
    {
        'title': 'org1',
        'name': 'Org1',
        'domain': 'icdoit.com',
        'mspid': 'Org1MSP',
        'peers': {
            'ips': ['192.168.12.76', '192.168.12.77'],
            'ports': [7051, 7052, 7053],
            'db': {
                "port": 5984,
                "user": "couchdb",
                "password": "couchdb",
            },
            'anchor_peers': [
                {
                    'ip': '192.168.12.76',
                    'host': 'peer0.org1.icdoit.com',
                    'port': 7051
                }
            ]
        },
    },
    {
        'title': 'org2',
        'name': 'Org2',
        'domain': 'test.com',
        'mspid': 'Org2MSP',
        'peers': {
            'ips': ['192.168.12.78'],
            'ports': [7051, 7052, 7053],
            'db': {
                "port": 5984,
                "user": "couchdb",
                "password": "couchdb",
            },
            'anchor_peers': [
                {
                    'ip': '192.168.12.78',
                    'host': 'peer0.org2.test.com',
                    'port': 7051
                }
            ]
        }
    }
]
