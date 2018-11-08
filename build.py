# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/6
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import os
import platform
import shutil

from jinja2 import Environment, PackageLoader

path = os.path.dirname(os.path.realpath(__file__))
deploy_path = path + "/deploy/"

env = Environment(loader=PackageLoader('templates', 'docker'))
f_env = Environment(loader=PackageLoader('templates', 'fabric'))
b_env = Environment(loader=PackageLoader('templates', 'bash'))

"""
部署要求：同一台机器内不能部署两个机构数据
"""

orderer_config = {
    'name': 'Orderer',
    'mspid': 'OrdererMSP',
    'domain': 'icdoit.com',
    'ips': ['10.0.0.23', '10.0.0.24'],
    'ports': [7050],
    'hosts': ['orderer1', 'orderer2'],
    'zookeeper': {
        'ips': ['10.0.0.21', '10.0.0.22', '10.0.0.23'],
        'ports': [2181, 2888, 3888]
    },
    'kafka': {
        'ips': ['10.0.0.21', '10.0.0.22', '10.0.0.23', '10.0.0.24'],
        'ports': [9092]
    },
}

org_config = [
    {
        'title': 'org1',
        'name': 'Org1',
        'domain': 'icdoit.com',
        'mspid': 'Org1MSP',
        'peer': {
            'ips': ['10.0.0.21', '10.0.0.22'],
            'ports': [7051, 7052, 7053],
            'db': {
                "port": 5984,
                "user": "couchdb",
                "password": "couchdb",
            },
            'anchor_peers': [
                {
                    'host': 'peer0.org1.icdoit.com',
                    'port': 7051
                }
            ]
        }
    },
    {
        'title': 'org2',
        'name': 'Org2',
        'domain': 'test.com',
        'mspid': 'Org2MSP',
        'peer': {
            'ips': ['10.0.0.24'],
            'ports': [7051, 7052, 7053],
            'db': {
                "port": 5984,
                "user": "couchdb",
                "password": "couchdb",
            },
            'anchor_peers': [
                {
                    'host': 'peer0.org2.test.com',
                    'port': 7051
                }
            ]
        }
    }
]


def __get_zk_hosts():
    zk_org = orderer_config['zookeeper']

    zk_hosts = []
    for i in range(0, len(zk_org['ips'])):
        zk_hosts.append(
            "z%d:%s" % (i + 1, zk_org['ips'][i])
        )

    return zk_hosts


def __get_kafka_hosts():
    k_org = orderer_config['kafka']

    k_hosts = []
    for i in range(0, len(k_org['ips'])):
        k_hosts.append(
            "k%d:%s" % (i + 1, k_org['ips'][i])
        )

    return k_hosts


def __get_kafka_ports():
    k_org = orderer_config['kafka']

    k_ports = []
    for i in range(0, len(k_org['ips'])):
        k_ports.append(
            "k%d:%s" % (i + 1, k_org['ports'][0])
        )

    return k_ports


def __get_orderer_hosts():
    orderer_hosts = []
    for i in range(0, len(orderer_config['ips'])):
        name = "orderer%d.%s" % (i + 1, orderer_config['domain'])
        orderer_hosts.append(
            "%s:%s" % (name, orderer_config['ips'][i])
        )

    return orderer_hosts


def __get_orderer_addresses():
    orderer_hosts = []
    for i in range(0, len(orderer_config['ips'])):
        name = "orderer%d.%s" % (i + 1, orderer_config['domain'])
        orderer_hosts.append(
            "%s:%s" % (name, orderer_config['ports'][0])
        )

    return orderer_hosts


def __save_file(folder, name, content):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f = open(folder + "/" + name, "w")
    f.write(content)
    f.close()


def build_zk_kafka_config(org):
    zk_org = orderer_config['zookeeper']
    zookeeper_list = []
    for i in range(0, len(zk_org['ips'])):
        id = i + 1
        zookeeper_list.append(
            {
                'id': id,
                'name': 'z%d' % id,
                'ip': zk_org['ips'][i],
                'port0': zk_org['ports'][0],
                'port1': zk_org['ports'][1],
                'port2': zk_org['ports'][2],
                'volumes': ['/opt/chainData/zookeeper/z%d/:/data/' % id],
                'ports': ['%s:%s' % (port, port) for port in zk_org['ports']]
            }
        )

    tmpl = env.get_template('docker-zk.yaml.tmpl')

    for zk in zookeeper_list:
        result = tmpl.render(
            zk=zk,
            zoo_servers=" ".join(["server.%(id)d=%(name)s:%(port1)d:%(port2)d" % zk for zk in zookeeper_list]),
            zk_hosts=__get_zk_hosts()
        )
        folder = deploy_path + "/%s/%s" % (org['title'], zk['ip'])
        __save_file(folder, "docker-zk.yaml", result)

    kafka_list = []
    k_org = orderer_config['kafka']
    for i in range(0, len(k_org['ips'])):
        id = i + 1
        kafka_list.append(
            {
                'id': id,
                'name': 'k%d' % id,
                'ip': k_org['ips'][i],
                'port': k_org['ports'][0],
                'volumes': ['/opt/chainData/kafka/k%d/:/data/' % id],
                'ports': ['%s:%s' % (port, port) for port in k_org['ports']]
            }
        )

    tmpl = env.get_template('docker-kafka.yaml.tmpl')

    for k in kafka_list:
        result = tmpl.render(
            k=k,
            zoo_servers=",".join(["%(name)s:%(port0)d" % zk for zk in zookeeper_list]),
            zk_hosts=__get_zk_hosts(),
            kafka_hosts=__get_kafka_hosts()
        )
        folder = deploy_path + "/%s/%s" % (org['title'], k['ip'])
        __save_file(folder, "docker-kafka.yaml", result)


def build_orderer_config(org):
    orderer_list = []

    domain = orderer_config['domain']
    for i in range(0, len(orderer_config['ips'])):
        id = i + 1
        orderer_list.append({
            "id": id,
            "domain": domain,
            "name": "orderer%d.%s" % (id, domain),
            "ip": orderer_config['ips'][i],
            'port': orderer_config['ports'][0],
            'mspid': org['mspid'],
            'ports': ['%s:%s' % (port, port) for port in orderer_config['ports']],
            'volumes': [
                '/opt/chainData/orderer/orderer%d/:/var/hyperledger/production/' % id,
                './channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block',
                './crypto-config/ordererOrganizations/%s/orderers/orderer%d.%s/msp:/var/hyperledger/orderer/msp' % (
                    domain, id, domain),
                './crypto-config/ordererOrganizations/%s/orderers/orderer%i.%s/tls:/var/hyperledger/orderer/tls' % (
                    domain, id, domain),
            ]
        })

    tmpl = env.get_template('docker-compose-orderer.yaml.tmpl')

    for orderer in orderer_list:
        result = tmpl.render(
            o=orderer,
            orderer_hosts=["%(name)s:%(ip)s" % orderer for orderer in orderer_list],
            zk_hosts=__get_zk_hosts(),
            kafka_hosts=__get_kafka_hosts(),
            kafka_ports=",".join(__get_kafka_ports())
        )
        folder = deploy_path + "/%s/%s" % (org['title'], orderer['ip'])
        __save_file(folder, "docker-compose-orderer.yaml", result)


def build_peer_config(org):
    peer_list = []

    domain = org['domain']
    peer_org = org['peer']
    for i in range(0, len(org['peer']['ips'])):
        id = i
        peer_list.append(
            {
                "id": id,
                "domain": domain,
                "name": "peer%d.%s" % (id, domain),
                "port0": peer_org['ports'][0],
                "port1": peer_org['ports'][1],
                "ip": peer_org['ips'][i],
                'network': 'net',
                'mspid': org['mspid'],
                'ports': ['%s:%s' % (port, port) for port in peer_org['ports']],
                'volumes': [
                    '/var/run/:/host/var/run/',
                    '/opt/chainData/peer/peer%d:/var/hyperledger/production' % id,
                    './crypto-config/peerOrganizations/%s.%s/peers/peer%d.%s.%s/msp:/etc/hyperledger/fabric/msp' % (
                        org['title'], domain, id, org['title'], domain),
                    './crypto-config/peerOrganizations/%s.%s/peers/peer%d.%s.%s/tls:/etc/hyperledger/fabric/tls' % (
                        org['title'], domain, id, org['title'], domain),
                ],
                "db": {
                    "name": "couchdb%d.%s" % (id, domain),
                    "ip": peer_org['ips'][i],
                    "port": peer_org['db']['port'],
                    "user": peer_org['db']['user'],
                    "password": peer_org['db']['password'],
                    'volumes': [
                        '/opt/chainData/couchdb/couchdb%d:/opt/couchdb/data' % id,
                    ]
                }
            }
        )

    tmpl = env.get_template('docker-compose-peer.yaml.tmpl')

    for peer in peer_list:
        result = tmpl.render(
            p=peer,
            orderer_hosts=__get_orderer_hosts(),
            peer_hosts=["%(name)s:%(ip)s" % peer for peer in peer_list],
            couchdb_hosts=["%(name)s:%(ip)s" % peer['db'] for peer in peer_list]
        )

        folder = deploy_path + "/%s/%s" % (org['title'], peer['ip'])
        __save_file(folder, "docker-compose-peer.yaml", result)


def build_crypto_config():
    tmpl = f_env.get_template('crypto-config.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_config,
        org_list=org_config,
    )
    __save_file(deploy_path, "crypto-config.yaml", result)


def build_configtx_config():
    tmpl = f_env.get_template('configtx.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_config,
        org_list=org_config,
        orderer_addresses=__get_orderer_addresses(),
        kafka_brokers=__get_kafka_ports(),
    )
    __save_file(deploy_path, "configtx.yaml", result)


def build_generate_bash():
    tmpl = b_env.get_template('generateArtifacts.sh.tmpl')

    result = tmpl.render(
        org_list=org_config,
    )
    __save_file(deploy_path, "generateArtifacts.sh", result)


def deploy():
    if os.path.isdir(deploy_path):
        shutil.rmtree(deploy_path)
        os.makedirs(deploy_path)

    folders = [deploy_path + "/channel-artifacts", deploy_path + "/crypto-config"]
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)

    if platform.platform().split("-")[0] == "Darwin":
        shutil.copytree(path + "/templates/bin/Darwin", deploy_path + "bin")
    else:
        shutil.copytree(path + "/templates/bin/linux", deploy_path + "bin")

    for org in org_config:
        build_zk_kafka_config(org)
        build_orderer_config(org)
        build_peer_config(org)
    build_crypto_config()
    build_configtx_config()
    build_generate_bash()

    print("#########  generateArtifacts ##############\n")
    os.system("cd deploy && sh generateArtifacts.sh")

    print("#########  Copy File ##############\n")
    # 复制生成好的crypto-config和channel-artifacts
    for org in org_config:
        for folder in os.listdir(deploy_path + org['title']):
            shutil.copytree(deploy_path + "channel-artifacts", "%s/%s/channel-artifacts" % (deploy_path + org['title'], folder))
            shutil.copytree(deploy_path + "crypto-config", "%s/%s/crypto-config" % (deploy_path + org['title'], folder))
            shutil.copy(deploy_path + "crypto-config.yaml", "%s/%s" % (deploy_path + org['title'], folder))
            shutil.copy(deploy_path + "configtx.yaml", "%s/%s" % (deploy_path + org['title'], folder))

    print("#########  Copy Finish ##############\n")


deploy()
