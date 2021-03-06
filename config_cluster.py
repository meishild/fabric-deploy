# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/14
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
channel_name = 'mychannel'
default_net = 'net'
volumes_path = "/opt/chainData"

zookeeper_tmpl_config = {
    # 机器配置只需配置ip和端口，一台机机器多个zk需要端口不同
    # 只支持单机器部署，以及完全多机器部署，不要在同时使用
    'machines': [
        {'ip': '192.168.12.74', 'port': 2181},
        {'ip': '192.168.12.75', 'port': 2181},
        {'ip': '192.168.12.76', 'port': 2181},
    ],
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
}

kafka_tmpl_config = {
    # 机器配置只需配置ip和端口，一台机机器多个zk需要端口不同
    # 只支持单机器部署，以及完全多机器部署，不要在同时使用
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
        {'ip': '192.168.12.75', 'port': '7050', }
    ],
    'type': 'kafka',
    'kafka': kafka_tmpl_config,
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
    'tls': True,
}

org1_peers_tmpl_config = {
    'machines': [
        {
            'ip': '192.168.12.76',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": {
                    'ip': '192.168.12.76',
                    "port": 5984,
                    "user": "couchdb",
                    "password": "couchdb",
                }
            },
            'ca': {
                'type': 'fabric-ca',
                'fabric-ca': {
                    'name': 'ca',
                    'ip': '192.168.12.76',
                    'port': 7054,
                    'admin': {
                        'username': 'admin',
                        'password': 'admin',
                    }
                }
            },
            'explorer': {
                'client_name': 'c_name',
                'ip': '192.168.12.74',
                'port': '8090',
                'pg_db': {
                    'name': 'fabric-explorer-pg',
                    'ip': '192.168.12.74',
                    'port': 5432,
                    'database': 'fabricexplorer',
                    'username': 'hppoc',
                    'password': 'password'
                }
            },
            'is_anchor_peer': True,
            'tls': True
        },
        {
            'ip': '192.168.12.77',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": {
                    'ip': '192.168.12.77',
                    "port": 5984,
                    "user": "couchdb",
                    "password": "couchdb",
                }
            },
            'is_anchor_peer': False,
            'tls': True
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
                "couch_db": {
                    'ip': '192.168.12.78',
                    "port": 5984,
                    "user": "couchdb",
                    "password": "couchdb",
                }
            },
            'is_anchor_peer': True,
            'tls': True
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
