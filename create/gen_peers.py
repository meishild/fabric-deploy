# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018-11-20
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
from config import *


def __build_couchdb_config(org_list):
    for org in org_list:
        for ip, db_list in org['db_ip_dicts'].items():
            result = env.get_template('docker-compose-couchdb.yaml.tmpl').render(
                dbs=db_list,
                network='net',
            )
            folder = machine_path + "/%s/%s" % (org['title'], ip)
            save_file(folder, "docker-compose-couchdb.yaml", result)

            peer_bash = b_env.get_template('initCouchDB.sh.tmpl').render(
                network='net',
                volume="%s/couchdb" % volumes_path
            )
            save_file(folder + "/scripts", "initCouchDB.sh", peer_bash)


def __build_peer_config(org_list, orderer_dict):
    for org in org_list:
        for ip, peer_list in org['peer_ip_dicts'].items():
            result = env.get_template('docker-compose-peer.yaml.tmpl').render(
                peers=peer_list,
                orderer_hosts=orderer_dict['orderer']['orderer_hosts'],
                peer_hosts=org['peer_hosts'],
                network='net'
            )

            folder = machine_path + "/%s/%s" % (org['title'], ip)
            save_file(folder, "docker-compose-peer.yaml", result)

            result = env.get_template('docker-compose-cli.yaml.tmpl').render(
                p=peer_list[0],
                orderer_hosts=orderer_dict['orderer']['orderer_hosts'],
                peer_hosts=org['peer_hosts'],
                network='net'
            )

            folder = machine_path + "/%s/%s" % (org['title'], ip)
            save_file(folder, "docker-compose-cli.yaml", result)


def __build_ca_config(org_list):
    for org in org_list:
        for ip, ca_list in org['ca_ip_dicts'].items():
            if len(ca_list) == 0:
                continue
            ca = ca_list[0].copy()
            file_list = os.listdir(deploy_path + "crypto-config/peerOrganizations/%s.%s/ca" % (org['title'], org['domain']))
            for name in file_list:
                if '_sk' in name:
                    ca['private_key'] = name
            ca['domain'] = org['domain']
            result = env.get_template('docker-compose-ca.yaml.tmpl').render(
                ca=ca,
            )

            folder = machine_path + "/%s/%s" % (org['title'], ip)
            save_file(folder, "docker-compose-ca.yaml", result)


def build_peer_config(orderer_dict, org_list):
    __build_couchdb_config(org_list)
    __build_peer_config(org_list, orderer_dict)
    __build_ca_config(org_list)
