# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/14
# version         :1.0
# python_version  :3.4.3
# description     : 本地开发网络
# ==============================================================================
channel_name = 'mychannel'
default_net = 'net'
volumes_path = ".tmp"
ip_addr = "192.168.100.99"

orderer_tmpl_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'shuwen.com',
    'machines': [
        {'ip': ip_addr, 'port': '7050'},
    ],
    'type': 'solo',
    # 是否需要独立部署，如果不需要配置机器即可，不会生成配置
    'is_need_gen': True,
    'tls': False
}

org1_peers_tmpl_config = {
    'machines': [
        {
            'ip': ip_addr,
            'ports': [7051, 7052, 7053],
            'db': {
                "type": 'level_db',
            },
            'is_anchor_peer': True,
            'tls': False,
            'mode': 'dev'
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

org_tmpl_list = [
    org1_tmpl_config,
]
