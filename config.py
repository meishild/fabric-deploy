# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/14
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import os

from jinja2 import Environment, PackageLoader

volumes_path = "/opt/chainData"

path = os.path.dirname(os.path.realpath(__file__))
deploy_path = path + "/deploy/"
machine_path = path + "/machine/"

env = Environment(loader=PackageLoader('templates', 'docker'))
f_env = Environment(loader=PackageLoader('templates', 'fabric'))
b_env = Environment(loader=PackageLoader('templates', 'bash'))

zookeeper_tmpl_config = {
    'machines': [
        {'ip': '192.168.12.74', 'ports': [2181, 2888, 3888]},
        {'ip': '192.168.12.75', 'ports': [2181, 2888, 3888]},
        {'ip': '192.168.12.76', 'ports': [2181, 2888, 3888]},
    ],
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True
}

kafka_tmpl_config = {
    'machines': [
        {'ip': '192.168.12.74', 'port': 9092},
        {'ip': '192.168.12.75', 'port': 9092},
        {'ip': '192.168.12.76', 'port': 9092},
        {'ip': '192.168.12.77', 'port': 9092},
    ],
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
    'zookeeper': zookeeper_tmpl_config
}

orderer_tmpl_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'shuwen.com',
    'machines': [
        {'ip': '192.168.12.74', 'port': '7050', },
        {'ip': '192.168.12.74', 'port': '8050', }
    ],
    'type': 'kafka',
    'kafka': kafka_tmpl_config,
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
}

couch_db_local = {
    'ip': '127.0.0.1',
    "port": 5984,
    "user": "couchdb",
    "password": "couchdb",
}

ca_config = {
    'name': 'ca',
    'ip': '192.168.12.74',
    'port': 7054,
    'admin': {
        'username': 'admin',
        'password': 'admin',
    }
}

org1_peers_tmpl_config = {
    'machines': [
        {
            'ip': '192.168.12.76',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": couch_db_local
            },
            'ca': {
                'type': 'fabric-ca',
                'fabric-ca': ca_config
            },
            'is_anchor_peer': True
        },
        {
            'ip': '192.168.12.77',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": couch_db_local
            },
            'is_anchor_peer': False
        },
    ]
}

org2_peers_tmpl_config = {
    'machines': [
        {
            'ip': '192.168.12.78',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": couch_db_local
            },
            'is_anchor_peer': True
        }
    ]
}

org1_tmpl_config = {
    'title': 'org1',
    'name': 'Org1',
    'domain': 'icdoit.com',
    'mspid': 'Org1MSP',
    'peers': org1_peers_tmpl_config
}

org2_tmpl_config = {
    'title': 'org2',
    'name': 'Org2',
    'domain': 'test.com',
    'mspid': 'Org2MSP',
    'peers': org2_peers_tmpl_config
}

org_tmpl_list = [
    org1_tmpl_config,
    org2_tmpl_config
]


def save_file(folder, name, content):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f = open(folder + "/" + name, "w")
    f.write(content)
    f.close()
