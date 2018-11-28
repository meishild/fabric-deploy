# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018/11/6
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import shutil
import sys

import init_config
from config import *
from create import gen_peers, gen_artifacts, gen_orderers

orderer_config = {}
org_list = []


def init_cfg():
    global orderer_config, org_list
    orderer_config = init_config.init_orderer_config(orderer_tmpl_config)
    org_list = init_config.init_peer_list_config(org_cfg_list=org_tmpl_list)


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
    if len(argv) == 2:
        deploy(argv[1] == "clean")
    else:
        deploy(False)
