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
import sys

from jinja2 import Environment, PackageLoader
from config import *

path = os.path.dirname(os.path.realpath(__file__))
deploy_path = path + "/deploy/"
machine_path = path + "/machine/"

env = Environment(loader=PackageLoader('templates', 'docker'))
f_env = Environment(loader=PackageLoader('templates', 'fabric'))
b_env = Environment(loader=PackageLoader('templates', 'bash'))

orderer_config = {}


def __save_file(folder, name, content):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    f = open(folder + "/" + name, "w")
    f.write(content)
    f.close()


def __init_orderer_config(orderer_cfg):
    orderer_list = []
    domain = orderer_cfg['domain']
    for i in range(0, len(orderer_cfg['ips'])):
        id = i + 1
        orderer_list.append({
            "id": id,
            "domain": domain,
            "name": "orderer%d.%s" % (id, domain),
            "ip": orderer_cfg['ips'][i],
            'port': orderer_cfg['ports'][0],
            'mspid': orderer_cfg['mspid'],
            'ports': ['%s:%s' % (port, port) for port in orderer_cfg['ports']],
            'volumes': [
                '%s/orderer/orderer%d/:/var/hyperledger/production/' % (volumes_path, id),
                './channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block',
                './crypto-config/ordererOrganizations/%s/orderers/orderer%d.%s/msp:/var/hyperledger/orderer/msp' % (
                    domain, id, domain),
                './crypto-config/ordererOrganizations/%s/orderers/orderer%i.%s/tls:/var/hyperledger/orderer/tls' % (
                    domain, id, domain),
            ]
        })

    zk_org = orderer_cfg['zookeeper']
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
                'volumes': ['%s/zookeeper/z%d/:/data/' % (volumes_path, id)],
                'ports': ['%s:%s' % (port, port) for port in zk_org['ports']]
            }
        )

    kafka_list = []
    k_org = orderer_cfg['kafka']
    for i in range(0, len(k_org['ips'])):
        id = i + 1
        kafka_list.append(
            {
                'id': id,
                'name': 'k%d' % id,
                'ip': k_org['ips'][i],
                'port': k_org['ports'][0],
                'volumes': ['%s/kafka/k%d/:/data/' % (volumes_path, id)],
                'ports': ['%s:%s' % (port, port) for port in k_org['ports']]
            }
        )

    """
    按照name:ip方式生成zkhost结构
    z1:10.0.0.x
    k1:10.0.0.x
    orderer1:10.0.0.x
    """
    zk_hosts = []
    for i in range(0, len(orderer_cfg['zookeeper']['ips'])):
        zk_hosts.append("z%d:%s" % (i + 1, orderer_cfg['zookeeper']['ips'][i]))

    k_hosts = []
    k_ports = []
    for i in range(0, len(orderer_cfg['kafka']['ips'])):
        k_hosts.append("k%d:%s" % (i + 1, orderer_cfg['kafka']['ips'][i]))
        k_ports.append("k%d:%s" % (i + 1, orderer_cfg['kafka']['ports'][0]))

    orderer_hosts = []
    orderer_ports = []
    orderer_address = []
    for i in range(0, len(orderer_cfg['ips'])):
        orderer_hosts.append("orderer%d.%s:%s" % (i + 1, domain, orderer_cfg['ips'][i]))
        orderer_ports.append("orderer%d.%s:%s" % (i + 1, domain, orderer_cfg['ports'][0]))
        orderer_address.append("orderer%d.%s" % (i + 1, domain))

    global orderer_config
    orderer_config = {
        'orderer': {
            'list': orderer_list,
            'orderer_hosts': orderer_hosts,
            'orderer_ports': orderer_ports,
            'orderer_address': orderer_address,
            'name': orderer_cfg['name'],
            'mspid': orderer_cfg['mspid'],
            'domain': orderer_cfg['domain'],
        },
        'zookeeper': {
            'list': zookeeper_list,
            'zk_hosts': zk_hosts,
            'ips': orderer_cfg['zookeeper']['ips'],
            'ports': orderer_cfg['zookeeper']['ports'],
        },
        'kafka': {
            'list': kafka_list,
            'kafka_hosts': k_hosts,
            'kafka_ports': k_ports,
            'ips': orderer_cfg['kafka']['ips'],
            'ports': orderer_cfg['kafka']['ports'],
        }
    }


def build_orderer_config():
    tmpl = env.get_template('docker-zk.yaml.tmpl')

    zookeeper_list = orderer_config['zookeeper']['list']
    for zk in zookeeper_list:
        result = tmpl.render(
            zk=zk,
            zoo_servers=" ".join(["server.%(id)d=%(name)s:%(port1)d:%(port2)d" % zk for zk in zookeeper_list]),
            zk_hosts=orderer_config['zookeeper']['zk_hosts']
        )
        folder = machine_path + "/orderer/%s" % zk['ip']
        __save_file(folder, "docker-zk.yaml", result)

    tmpl = env.get_template('docker-kafka.yaml.tmpl')

    for k in orderer_config['kafka']['list']:
        result = tmpl.render(
            k=k,
            zoo_servers=",".join(["%(name)s:%(port0)d" % zk for zk in zookeeper_list]),
            zk_hosts=orderer_config['zookeeper']['zk_hosts'],
            kafka_hosts=orderer_config['kafka']['kafka_hosts']
        )
        folder = machine_path + "/orderer/%s" % k['ip']
        __save_file(folder, "docker-kafka.yaml", result)

    tmpl = env.get_template('docker-compose-orderer.yaml.tmpl')

    orderer_list = orderer_config['orderer']['list']
    for orderer in orderer_list:
        result = tmpl.render(
            o=orderer,
            orderer_hosts=orderer_config['orderer']['orderer_hosts'],
            zk_hosts=orderer_config['zookeeper']['zk_hosts'],
            kafka_hosts=orderer_config['kafka']['kafka_hosts'],
            kafka_ports=",".join(orderer_config['kafka']['kafka_ports'])
        )
        folder = machine_path + "/orderer/%s" % orderer['ip']
        __save_file(folder, "docker-compose-orderer.yaml", result)


org_peer_list = []


def __init_peer_config(peer_cfg_list):
    global org_peer_list
    for peer_org in peer_cfg_list:
        domain = "%s.%s" % (peer_org['title'], peer_org['domain'])
        peers = peer_org['peers']
        peer_list = []
        for i in range(0, len(peer_org['peers']['ips'])):
            id = i
            peer_tmp_dict = {
                "id": id,
                "domain": domain,
                "name": "peer%d.%s" % (id, domain),
                "port0": peers['ports'][0],
                "port1": peers['ports'][1],
                "ip": peers['ips'][i],
                'network': 'net',
                'mspid': peer_org['mspid'],
                'ports': ['%s:%s' % (port, port) for port in peers['ports']],
                'volumes': [
                    '/var/run/:/host/var/run/',
                    '%s/peer/peer%d:/var/hyperledger/production' % (volumes_path, id),
                    './crypto-config/peerOrganizations/%s/peers/peer%d.%s/msp:/etc/hyperledger/fabric/msp' % (
                        domain, id, domain),
                    './crypto-config/peerOrganizations/%s/peers/peer%d.%s/tls:/etc/hyperledger/fabric/tls' % (
                        domain, id, domain),
                ],
            }
            if 'db' in peers:
                peer_tmp_dict['db'] = {
                    "id": id,
                    "name": "couchdb%d.%s" % (id, domain),
                    "ip": peers['ips'][i],
                    "port": peers['db']['port'],
                    "user": peers['db']['user'],
                    "password": peers['db']['password'],
                    'volumes': [
                        '%s/couchdb/couchdb%d:/opt/couchdb/data' % (volumes_path, id),
                    ]
                }
            if 'ca' in peer_org:
                peer_tmp_dict['ca'] = {
                    'name': "ca.%s" % domain,
                    'ip': peer_org['ca']['ip'],
                    'port': peer_org['ca']['port'],
                    'admin': peer_org['ca']['admin'],
                }
            peer_list.append(peer_tmp_dict)
        org_peer_list.append({
            'list': peer_list,
            'title': peer_org['title'],
            'name': peer_org['name'],
            'domain': peer_org['domain'],
            'mspid': peer_org['mspid'],
            'anchor_peers': peers['anchor_peers'],
        })


def build_peer_config():
    for org_peer in org_peer_list:
        for peer in org_peer['list']:
            result = env.get_template('docker-compose-peer.yaml.tmpl').render(
                p=peer,
                orderer_hosts=orderer_config['orderer']['orderer_hosts'],
                peer_hosts=["%(name)s:%(ip)s" % peer for peer in org_peer['list']],
                couchdb_hosts=["%(name)s:%(ip)s" % peer['db'] for peer in org_peer['list']],
            )

            folder = machine_path + "/%s/%s" % (org_peer['title'], peer['ip'])
            __save_file(folder, "docker-compose-peer.yaml", result)

            peer_bash = b_env.get_template('initPeer.sh.tmpl').render(
                p=peer,
                volume="%s/couchdb/couchdb%d" % (volumes_path, peer['id'])
            )
            __save_file(folder + "/scripts", "initPeer.sh", peer_bash)


def build_ca():
    for peer_org in org_peer_list:
        for peer in peer_org['list']:
            if 'ca' not in peer:
                continue
            ca = peer['ca'].copy()
            file_list = os.listdir(deploy_path + "crypto-config/peerOrganizations/" + peer['domain'] + "/ca")
            for name in file_list:
                if '_sk' in name:
                    ca['private_key'] = name
            ca['domain'] = peer['domain']
            result = env.get_template('docker-compose-ca.yaml.tmpl').render(
                ca=ca,
            )

            folder = machine_path + "/%s/%s" % (peer_org['title'], peer['ip'])
            __save_file(folder, "docker-compose-ca.yaml", result)


def build_crypto_config():
    tmpl = f_env.get_template('crypto-config.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_config['orderer'],
        org_list=org_peer_list,
    )
    __save_file(deploy_path, "crypto-config.yaml", result)


def build_configtx_config():
    tmpl = f_env.get_template('configtx.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_config['orderer'],
        org_list=org_peer_list,
        orderer_addresses=orderer_config['orderer']['orderer_ports'],
        kafka_brokers=orderer_config['kafka']['kafka_ports'],
    )
    __save_file(deploy_path, "configtx.yaml", result)


def build_generate_bash():
    tmpl = b_env.get_template('generateArtifacts.sh.tmpl')

    result = tmpl.render(
        org_list=org_peer_list,
    )
    __save_file(deploy_path, "generateArtifacts.sh", result)


def generate_artifacts_and_crypto():
    print("#########  generate artifacts and crypto config ##############\n")

    if os.path.isdir(deploy_path):
        shutil.rmtree(deploy_path)
        os.makedirs(deploy_path)

    folders = [deploy_path + "/channel-artifacts", deploy_path + "/crypto-config"]
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)

    build_crypto_config()
    build_configtx_config()
    build_generate_bash()
    print("#########  generate artifacts ##############\n")
    if platform.platform().split("-")[0] == "Darwin":
        shutil.copytree(path + "/templates/bin/Darwin", deploy_path + "bin")
    else:
        shutil.copytree(path + "/templates/bin/linux", deploy_path + "bin")

    os.system("cd %s && sh generateArtifacts.sh" % deploy_path)
    print("#########  finish generate artifacts and crypto config ##############\n")


def generate_machine():
    print("#########  generate machine config ##############\n")
    if os.path.isdir(machine_path):
        shutil.rmtree(machine_path)
        os.makedirs(machine_path)

    build_orderer_config()
    build_peer_config()
    build_ca()
    print("#########  copy machine file ##############\n")

    # 复制生成好的crypto-config和channel-artifacts
    for org in org_peer_list:
        for folder in os.listdir(machine_path + org['title']):
            to = machine_path + org['title'] + "/" + folder
            __copy(to)
            if folder == org['anchor_peers'][0]['ip']:
                shutil.copytree(path + "/templates/chaincode/", to + "/chaincode")

    for folder in os.listdir(machine_path + "orderer"):
        __copy(machine_path + "/orderer/" + folder)

    print("#########  machine finish ##############\n")


def __copy(to):
    shutil.copytree(deploy_path + "channel-artifacts", "%s/channel-artifacts" % to)
    shutil.copytree(deploy_path + "crypto-config", "%s/crypto-config" % to)
    shutil.copy(deploy_path + "crypto-config.yaml", "%s" % to)
    shutil.copy(deploy_path + "configtx.yaml", "%s" % to)


def deploy(need_generate=False):
    __init_orderer_config(orderer_tmpl_config)
    __init_peer_config(peer_tmpl_list)
    if need_generate:
        print("NEED GENERATE ARTIFACTS AND CRYPTO!!!!!")
        generate_artifacts_and_crypto()
    else:
        print("DON'T NEED GENERATE ARTIFACTS AND CRYPTO!!!!!")
    generate_machine()


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 2:
        deploy(argv[1] != "clean")
    else:
        deploy(True)
