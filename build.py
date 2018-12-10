# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/6
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import os
import shutil
import sys

import base_config
import init_config
from create import gen_peers, gen_artifacts, gen_orderers

orderer_config = {}
org_list = []
config_file = "config_byfn"
path = base_config.path
deploy_path = base_config.deploy_path
machine_path = base_config.machine_path


def init_cfg():
    if config_file is None:
        raise Exception("缺少配置文件")

    config_module = __import__(config_file)

    channel_name = getattr(config_module, "channel_name")
    default_net = getattr(config_module, "default_net")
    volumes_path = getattr(config_module, "volumes_path")

    orderer_tmpl_config = getattr(config_module, "orderer_tmpl_config")
    org_tmpl_list = getattr(config_module, "org_tmpl_list")
    global orderer_config, org_list
    init_config.init_config(volumes_path, default_net, channel_name)
    orderer_config = init_config.init_orderer_config(orderer_tmpl_config)
    org_list = init_config.init_peer_list_config(org_tmpl_list)


def generate_artifacts():
    if len(org_list) == 0:
        init_cfg()
    gen_artifacts.generate_artifacts_and_crypto(orderer_config, org_list)


def generate_machine():
    print("#########  generate machine config ##############\n")
    if os.path.isdir(machine_path):
        shutil.rmtree(machine_path)
        os.makedirs(machine_path)

    if len(org_list) == 0:
        init_cfg()

    gen_orderers.build_orderer_config(orderer_config)
    gen_peers.build_peer_config(orderer_config, org_list)

    print("#########  copy machine file ##############\n")

    # 复制生成好的crypto-config和channel-artifacts
    for org in org_list:
        for folder in os.listdir(machine_path + org['title']):
            to = machine_path + org['title'] + "/" + folder
            __copy(to)
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
    if need_generate:
        print("NEED GENERATE ARTIFACTS AND CRYPTO!!!!!")
        generate_artifacts()
    else:
        print("DON'T NEED GENERATE ARTIFACTS AND CRYPTO!!!!!")
    generate_machine()


if __name__ == '__main__':
    argv = sys.argv
    # config_file = 'config_cluster'
    config_file = "config_dev"
    if len(argv) == 2:
        deploy(argv[1] == "clean")
    else:
        deploy(False)
