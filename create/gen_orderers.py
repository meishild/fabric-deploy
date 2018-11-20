# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018-11-20
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
from config import *


def __build_zookeeper(orderer_config):
    tmpl = env.get_template('docker-zk.yaml.tmpl')
    if 'zookeeper' not in orderer_config:
        return

    if not orderer_config['zookeeper']['is_need_gen']:
        return

    for ip in orderer_config['zookeeper']['machines']:
        zk_list = orderer_config['zookeeper']['machines'][ip]
        result = tmpl.render(
            zk_list=zk_list,
            zoo_servers=orderer_config['zookeeper']['zoo_server'],
            zk_hosts=orderer_config['zookeeper']['zk_hosts']
        )
        folder = machine_path + "/orderer/%s" % ip
        save_file(folder, "docker-zk.yaml", result)


def __build_kafka(orderer_config):
    tmpl = env.get_template('docker-kafka.yaml.tmpl')
    if 'kafka' not in orderer_config:
        return

    if not orderer_config['kafka']['is_need_gen']:
        return

    for ip in orderer_config['kafka']['machines']:
        k_list = orderer_config['kafka']['machines'][ip]
        result = tmpl.render(
            k_list=k_list,
            zoo_servers=",".join(orderer_config['zookeeper']['zk_ports']),
            zk_hosts=orderer_config['zookeeper']['zk_hosts'],
            kafka_hosts=orderer_config['kafka']['k_hosts']
        )
        folder = machine_path + "/orderer/%s" % ip
        save_file(folder, "docker-zk.yaml", result)


def __build_orderer_config(orderer_config):
    tmpl = env.get_template('docker-compose-orderer.yaml.tmpl')
    if not orderer_config['orderer']['is_need_gen']:
        return
    orderer_ip_dicts = orderer_config['orderer']['orderer_ip_dicts']
    for ip in orderer_ip_dicts.keys():
        result = tmpl.render(
            orderer_list=orderer_ip_dicts[ip],
            orderer_hosts=orderer_config['orderer']['orderer_hosts'],
            zk_hosts=orderer_config['zookeeper']['zk_hosts'],
            kafka_hosts=orderer_config['kafka']['k_hosts'],
            kafka_ports=",".join(orderer_config['kafka']['k_ports'])
        )
        folder = machine_path + "/orderer/%s" % ip
        save_file(folder, "docker-compose-orderer.yaml", result)


def build_orderer_config(orderer_config):
    __build_zookeeper(orderer_config)
    __build_kafka(orderer_config)
    __build_orderer_config(orderer_config)
