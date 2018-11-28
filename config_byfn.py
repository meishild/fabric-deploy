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

orderer_tmpl_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'shuwen.com',
    'machines': [
        {'ip': '192.168.12.79', 'port': '70500', },
    ],
    'type': 'solo',
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
}

org1_peers_tmpl_config = {
    'machines': [
        {
            'ip': '192.168.12.79',
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": {
                    'ip': '192.168.12.76',
                    "port": 59840,
                    "user": "couchdb",
                    "password": "couchdb",
                }
            },
            'explorer': {
                'client_name': 'c_name',
                'ip': '192.168.12.79',
                'port': '8090',
                'pg_db': {
                    'name': 'fabric-explorer-pg',
                    'ip': '192.168.12.79',
                    'port': 54320,
                    'database': 'fabricexplorer',
                    'username': 'hppoc',
                    'password': 'password'
                }
            },
            'is_anchor_peer': True
        },
        {
            'ip': '192.168.12.79',
            'ports': [17051, 17052, 17053],
            'db': {
                "type": 'level_db',
            },
            'is_anchor_peer': False
        },
    ]
}

org2_peers_tmpl_config = {
    'machines': [
        {
            'ip': '192.168.12.79',
            'ports': [27051, 27052, 27053],
            'db': {
                "type": 'level_db',
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
