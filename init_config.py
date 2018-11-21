# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018-11-20
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
from config import *


def __init_zookeeper_config(zk_config):
    zk_list = zk_config['machines']
    zk_ip_dicts = {}
    zk_hosts = []
    zk_ports = []

    zoo_server_list = []
    for i in range(0, len(zk_list)):
        id = i + 1
        ip = zk_list[i]['ip']
        if ip not in zk_ip_dicts:
            zk_ip_dicts[ip] = []

        zk_ports.append("z%d:%s" % (i + 1, zk_list[i]['port']))
        zk_hosts.append("z%d:%s" % (i + 1, ip))
        zk_dict = {
            'id': id,
            'name': 'z%d' % id,
            'ip': ip,
            'port': zk_list[i]['port'],
            'volumes': ['%s/zookeeper/z%d/:/data/' % (volumes_path, id)],
            'ports': ["%d:2188" % zk_list[i]['port']],
        }

        zk_ip_dicts[ip].append(zk_dict)
        zoo_server_list.append("server.%(id)d=%(name)s:2888:3888" % zk_dict)
    return {
        'machines': zk_ip_dicts,
        'zk_hosts': zk_hosts,
        'zk_ports': zk_ports,
        'zoo_server': " ".join(zoo_server_list),
        'is_need_gen': zk_config['is_need_gen'],
        'single': zk_list[0]['ip'] == zk_list[1]['ip']
    }


def __init_kafka_config(kafka_config):
    k_hosts = []
    k_ports = []

    kafka_list = kafka_config['machines']
    zk_ip_dicts = {}

    for i in range(0, len(kafka_list)):
        id = i + 1
        ip = kafka_list[i]['ip']
        if ip not in zk_ip_dicts:
            zk_ip_dicts[ip] = []

        k_hosts.append("k%d:%s" % (i + 1, ip))
        k_ports.append("k%d:%s" % (i + 1, kafka_list[i]['port']))

        zk_ip_dicts[ip].append(
            {
                'id': id,
                'name': 'k%d' % id,
                'ip': ip,
                'port': kafka_list[i]['port'],
                'volumes': ['%s/kafka/k%d/:/data/' % (volumes_path, id)],
                'ports': ['%s:9092' % kafka_list[i]['port']]
            }
        )
    return {
        'machines': zk_ip_dicts,
        'k_hosts': k_hosts,
        'k_ports': k_ports,
        'is_need_gen': kafka_config['is_need_gen'],
        'single': kafka_list[0]['ip'] == kafka_list[1]['ip']
    }


def __init_orderer_config(orderer_cfg):
    orderer_ip_dicts = {}
    domain = orderer_cfg['domain']

    orderer_hosts = []
    orderer_ports = []
    orderer_address = []
    for i in range(0, len(orderer_cfg['machines'])):
        id = i + 1
        m_cfg = orderer_cfg['machines'][i]
        m_ip = m_cfg['ip']
        if m_ip not in orderer_ip_dicts:
            orderer_ip_dicts[m_ip] = []

        orderer_hosts.append("orderer%d.%s:%s" % (id, domain, m_cfg['ip']))
        orderer_ports.append("orderer%d.%s:%s" % (id, domain, m_cfg['port']))
        orderer_address.append("orderer%d" % id)

        orderer_ip_dicts[m_ip].append({
            "id": id,
            "domain": domain,
            "name": "orderer%d.%s" % (id, domain),
            "ip": m_cfg['ip'],
            'port': m_cfg['port'],
            'mspid': orderer_cfg['mspid'],
            'ports': ["%s:%s" % (m_cfg['port'], m_cfg['port'])],
            'volumes': [
                '%s/orderer/orderer%d/:/var/hyperledger/production/' % (volumes_path, id),
                './channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block',
                './crypto-config/ordererOrganizations/%s/orderers/orderer%d.%s/msp:/var/hyperledger/orderer/msp' % (
                    domain, id, domain),
                './crypto-config/ordererOrganizations/%s/orderers/orderer%i.%s/tls:/var/hyperledger/orderer/tls' % (
                    domain, id, domain),
            ]
        })
    orderer_config = {
        'orderer': {
            'orderer_ip_dicts': orderer_ip_dicts,
            'orderer_hosts': orderer_hosts,
            'orderer_ports': orderer_ports,
            'orderer_address': orderer_address,
            'name': orderer_cfg['name'],
            'mspid': orderer_cfg['mspid'],
            'domain': orderer_cfg['domain'],
            'is_need_gen': orderer_cfg['is_need_gen']
        }
    }

    if orderer_cfg['type'] == 'kafka':
        orderer_config['kafka'] = __init_kafka_config(kafka_config=orderer_cfg['kafka'])
        orderer_config['zookeeper'] = __init_zookeeper_config(zk_config=orderer_cfg['kafka']['zookeeper'])
    return orderer_config


def __init_couch_db(domain, db, id):
    return {
        "id": id,
        "name": "couchdb%d.%s" % (id, domain),
        "ip": db['ip'],
        "port": db['port'],
        "user": db['user'],
        "password": db['password'],
        'volumes': [
            '%s/couchdb/couchdb%d:/opt/couchdb/data' % (volumes_path, id),
        ]
    }


def __init_fabric_ca(domain, ca, id):
    return {
        'name': "ca%d.%s" % (id, domain),
        'ip': ca['ip'],
        'port': ca['port'],
        'admin': ca['admin'],
    }


def __init_org_peers_config(org):
    """

    :param org:
    :return:
    """

    peer_ip_dicts = {}
    db_ip_dicts = {}
    ca_ip_dicts = {}

    peer_hosts = []
    anchor_peers = []
    domain = "%s.%s" % (org['title'], org['domain'])
    for i in range(0, len(org['peers']['machines'])):
        machine = org['peers']['machines'][i]
        ip = machine['ip']
        if ip not in peer_ip_dicts:
            peer_ip_dicts[ip] = []
        if ip not in db_ip_dicts:
            db_ip_dicts[ip] = []
        if ip not in ca_ip_dicts:
            ca_ip_dicts[ip] = []
        id = i
        peer_dict = {
            "id": id,
            "domain": domain,
            "name": "peer%d.%s" % (id, domain),
            "port0": machine['ports'][0],
            "port1": machine['ports'][1],
            "ip": ip,
            'network': 'net',
            'mspid': org['mspid'],
            'ports': ['%s:%s' % (port, port) for port in machine['ports']],
            'volumes': [
                '/var/run/:/host/var/run/',
                '%s/peer/peer%d:/var/hyperledger/production' % (volumes_path, id),
                './crypto-config/peerOrganizations/%s/peers/peer%d.%s/msp:/etc/hyperledger/fabric/msp' % (
                    domain, id, domain),
                './crypto-config/peerOrganizations/%s/peers/peer%d.%s/tls:/etc/hyperledger/fabric/tls' % (
                    domain, id, domain),
            ],
        }
        peer_hosts.append("%(name)s:%(ip)s" % peer_dict)
        peer_ip_dicts[ip].append(peer_dict)

        if 'db' in machine and machine['db']['type'] == 'couch_db':
            db = machine['db']['couch_db']
            couch_db = __init_couch_db(domain, db, id)
            db_ip_dicts[ip].append(couch_db)
            peer_dict['db'] = couch_db

        if 'ca' in machine and machine['ca']['type'] == 'fabric-ca':
            ca = machine['ca']['fabric-ca']
            fabric_ca = __init_fabric_ca(domain, ca, id)
            ca_ip_dicts[ip].append(fabric_ca)
        if 'is_anchor_peer':
            anchor_peers.append({
                'host': peer_dict['name'],
                'port': peer_dict['port0'],
                'ip': peer_dict['ip']
            })

    return {
        'title': org['title'],
        'name': org['name'],
        'domain': org['domain'],
        'mspid': org['mspid'],
        'peer_ip_dicts': peer_ip_dicts,
        'db_ip_dicts': db_ip_dicts,
        'ca_ip_dicts': ca_ip_dicts,
        'peer_hosts': peer_hosts,
        'anchor_peers': anchor_peers,
    }


def __init_peer_config(org_cfg_list):
    org_peer_list = []
    for org in org_cfg_list:
        org_peer_list.append(__init_org_peers_config(org))
    return org_peer_list


def init_orderer_config(orderer_cfg):
    return __init_orderer_config(orderer_cfg)


def init_peer_list_config(org_cfg_list):
    """

    :param org_cfg_list:
    :return:
    [{
        'title': 'org1',
        'name': 'Org1',
        'domain': 'icdoit.com',
        'mspid': 'Org1MSP',
        'peer_ip_dicts': {
            '192.168.12.76': [{
                'id': 0,
                'domain': 'org1.icdoit.com',
                'name': 'peer0.org1.icdoit.com',
                'port0': 7051,
                'port1': 7052,
                'ip': '192.168.12.76',
                'network': 'net',
                'mspid': 'Org1MSP',
                'ports': ['7051:7051', '7052:7052', '7053:7053'],
                'volumes': ['/var/run/:/host/var/run/', '/opt/chainData/peer/peer0:/var/hyperledger/production',
                './crypto-config/peerOrganizations/org1.icdoit.com/peers/peer0.org1.icdoit.com/msp:/etc/hyperledger/fabric/msp',
                './crypto-config/peerOrganizations/org1.icdoit.com/peers/peer0.org1.icdoit.com/tls:/etc/hyperledger/fabric/tls']
            }, {
                'id': 1,
                'domain': 'org1.icdoit.com',
                'name': 'peer1.org1.icdoit.com',
                'port0': 7051,
                'port1': 7052,
                'ip': '192.168.12.76',
                'network': 'net',
                'mspid': 'Org1MSP',
                'ports': ['7051:7051', '7052:7052', '7053:7053'],
                'volumes': ['/var/run/:/host/var/run/', '/opt/chainData/peer/peer1:/var/hyperledger/production',
                './crypto-config/peerOrganizations/org1.icdoit.com/peers/peer1.org1.icdoit.com/msp:/etc/hyperledger/fabric/msp',
                './crypto-config/peerOrganizations/org1.icdoit.com/peers/peer1.org1.icdoit.com/tls:/etc/hyperledger/fabric/tls']
            }]
        },
        'db_ip_dicts': {
            '192.168.12.76': [{
                'id': 0,
                'name': 'couchdb0.org1.icdoit.com',
                'ip': '127.0.0.1',
                'port': 5984,
                'user': 'couchdb',
                'password': 'couchdb',
                'volumes': ['/opt/chainData/couchdb/couchdb0:/opt/couchdb/data']
            }]
        },
        'ca_ip_dicts': {
            '192.168.12.76': [{
                'name': 'ca0.org1.icdoit.com',
                'ip': '192.168.12.74',
                'port': 7054,
                'admin': {
                    'username': 'admin',
                    'password': 'admin'
                }
            }]
        }
    }, {
        'title': 'org2',
        'name': 'Org2',
        'domain': 'test.com',
        'mspid': 'Org2MSP',
        'peer_ip_dicts': {
            '192.168.12.78': [{
                'id': 0,
                'domain': 'org2.test.com',
                'name': 'peer0.org2.test.com',
                'port0': 7051,
                'port1': 7052,
                'ip': '192.168.12.78',
                'network': 'net',
                'mspid': 'Org2MSP',
                'ports': ['7051:7051', '7052:7052', '7053:7053'],
                'volumes': ['/var/run/:/host/var/run/', '/opt/chainData/peer/peer0:/var/hyperledger/production',
                './crypto-config/peerOrganizations/org2.test.com/peers/peer0.org2.test.com/msp:/etc/hyperledger/fabric/msp',
                './crypto-config/peerOrganizations/org2.test.com/peers/peer0.org2.test.com/tls:/etc/hyperledger/fabric/tls']
            }]
        },
        'db_ip_dicts': {
            '192.168.12.78': []
        },
        'ca_ip_dicts': {
            '192.168.12.78': []
        }
    }]

    """
    return __init_peer_config(org_cfg_list)
