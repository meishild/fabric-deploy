# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/14
# version         :1.0
# python_version  :3.4.3
# description     : byfn网络
# ==============================================================================
channel_name = 'mychannel'
default_net = 'net'
volumes_path = "/opt/chainData"

byfn_ip = "192.168.12.79"

orderer_tmpl_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'shuwen.com',
    'machines': [
        {'ip': byfn_ip, 'port': '7050', },
    ],
    'type': 'solo',
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
}

org1_peers_tmpl_config = {
    'machines': [
        {
            'ip': byfn_ip,
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'couch_db',
                "couch_db": {
                    'ip': byfn_ip,
                    "port": 5984,
                    "user": "couchdb",
                    "password": "couchdb",
                }
            },
            'explorer': {
                'client_name': 'c_name',
                'ip': byfn_ip,
                'port': '8090',
                'pg_db': {
                    'name': 'fabric-explorer-pg',
                    'ip': byfn_ip,
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
            'ip': byfn_ip,
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
