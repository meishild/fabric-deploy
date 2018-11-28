# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2018-11-20
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import platform
import shutil

from config import *


def build_crypto_config(orderer_cfg, org_list):
    tmpl = f_env.get_template('crypto-config.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_cfg['orderer'],
        org_list=org_list,
    )
    save_file(deploy_path, "crypto-config.yaml", result)


def build_configtx_config(orderer_cfg, org_list):
    tmpl = f_env.get_template('configtx.yaml.tmpl')

    result = tmpl.render(
        orderer=orderer_cfg['orderer'],
        org_list=org_list,
        kafka_brokers=orderer_cfg['kafka']['k_ip_ports'],
    )
    save_file(deploy_path, "configtx.yaml", result)


def generate_artifacts_and_crypto(orderer_config, org_list):
    print("#########  generate artifacts and crypto config ##############\n")

    if os.path.isdir(deploy_path):
        shutil.rmtree(deploy_path)
        os.makedirs(deploy_path)

    folders = [deploy_path + "/channel-artifacts", deploy_path + "/crypto-config"]
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)

    build_crypto_config(orderer_config, org_list)
    build_configtx_config(orderer_config, org_list)

    print("#########  generate artifacts ##############\n")
    if platform.platform().split("-")[0] == "Darwin":
        shutil.copytree(path + "/templates/bin/Darwin", deploy_path + "bin")
    else:
        shutil.copytree(path + "/templates/bin/linux", deploy_path + "bin")

    b_h = "cd %s && " % deploy_path
    print("Generate certificates using cryptogen tool\n")
    os.system("%s bin/cryptogen generate --config=./crypto-config.yaml" % b_h)

    print("Generating Orderer Genesis block\n")
    os.system("%s bin/configtxgen -profile TwoOrgsOrdererGenesis -outputBlock ./channel-artifacts/genesis.block" % b_h)

    print("Generating channel configuration transaction 'channel.tx'\n")
    gen_channel_bash = "%s bin/configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID %s"
    os.system(gen_channel_bash % (b_h, channel_name))
    for org in org_list:
        print("Generating anchor peer update for %s\n" % org['mspid'])
        bash = "%s bin/configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./channel-artifacts/%sanchors.tx -channelID %s " \
               "-asOrg %s"
        os.system(bash % (b_h, org['mspid'], channel_name, org['mspid']))
    print("#########  finish generate artifacts and crypto config ##############\n")
