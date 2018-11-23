# fabric生产部署快速脚本

v 0.0.1



## clean
docker stop $(docker ps -q) & docker rm $(docker ps -aq) && rm -fr /opt/chainData/ && docker network rm net

## cp
cd /home/fabric/ && rm -fr * && rm -fr /home/songhaiyang/machine.tar.gz

rm -fr machine.tar.gz && scp songhaiyang@06:/home/fabric/fabric-deploy/machine.tar.gz ./

scp machine.tar.gz songhaiyang@03: && scp machine.tar.gz songhaiyang@04: && scp machine.tar.gz songhaiyang@05: && scp machine.tar.gz songhaiyang@01: && scp machine.tar.gz songhaiyang@02:

cd /home/fabric && mv /home/songhaiyang/machine.tar.gz /home/fabric && tar zxvf machine.tar.gz


## 74
cd /home/fabric/machine/orderer/192.168.12.74/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d
docker exec -it z1 bin/zkServer.sh status
docker logs -f k1

## 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d
docker exec -it z2 bin/zkServer.sh status
## 76
cd /home/fabric/machine/orderer/192.168.12.76/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d
docker exec -it z3 bin/zkServer.sh status

## 77
cd /home/fabric/machine/orderer/192.168.12.77/ && docker-compose -f docker-kafka.yaml up -d
docker logs -f k4
===================== ZOOKEPPER & KAFKA Start Finish ===================== 

## 74
cd /home/fabric/machine/orderer/192.168.12.74/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer1.shuwen.com

## 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer2.shuwen.com

===================== ORDERER Start Finish ===================== 

## 76
cd /home/fabric/machine/org1/192.168.12.76/ && sh scripts/initCouchDB.sh && docker-compose -f docker-compose-peer.yaml up -d
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d

docker-compose -f docker-compose-ca.yaml up -d

===================== peer0.org1 PEER AND CA Start Finish ===================== 

## 77
cd /home/fabric/machine/org1/192.168.12.77/ && sh scripts/initCouchDB.sh
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d
docker logs -f peer1.org1.icdoit.com
===================== peer1.org1 PEER Start Finish ===================== 


## 78
cd /home/fabric/machine/org2/192.168.12.78/ && sh scripts/initCouchDB.sh
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d

===================== peer0.org2 PEER Start Finish ===================== 

# 76
docker exec -it cli peer channel create -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/channel.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem

===================== Channel 'mychannel' created =====================

docker exec -it cli cp mychannel.block scripts
docker exec -it cli peer channel join -b mychannel.block
===================== peer0.org1 joined channel 'mychannel' =====================

####
scp songhaiyang@01:/home/fabric/machine/org1/192.168.12.76/scripts/mychannel.block ./
scp mychannel.block songhaiyang@02: && scp mychannel.block songhaiyang@05:

===================== peer1.org1 joined channel 'mychannel' =====================
# 77
cp /home/songhaiyang/mychannel.block /home/fabric/machine/org1/192.168.12.77/scripts
docker exec -it cli peer channel join -b scripts/mychannel.block

===================== peer0.org2 joined channel 'mychannel' =====================
# 78
cp /home/songhaiyang/mychannel.block /home/fabric/machine/org2/192.168.12.78/scripts
docker exec -it cli peer channel join -b scripts/mychannel.block

===================== peer1.org1 joined channel 'mychannel' =====================


# 76
docker exec -it cli peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org1MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem
===================== Anchor peers updated for org 'Org1MSP' on channel 'mychannel' =====================

# 78
docker exec -it cli peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org2MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem
===================== Anchor peers updated for org 'Org2MSP' on channel 'mychannel' =====================


# 76
docker exec -it cli peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
===================== Chaincode is installed on peer0.org1 =====================

docker exec -it cli peer chaincode instantiate -o orderer1.shuwen.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem -C mychannel -n mycc -l java -v 1.0 -c '{"Args":["init","a","100","b","200"]}'  -P 'OR ('\''Org1MSP.peer'\'','\''Org2MSP.peer'\'')'
===================== Chaincode is instantiated on peer0.org1 on channel 'mychannel' =====================

docker exec -it cli peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'


# 78
docker exec -it cli peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
docker exec -it cli peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
===================== Chaincode is installed on peer0.org2 =====================





## BYLOG
Starting for channel 'mychannel' with CLI timeout of '10' seconds and CLI delay of '3' seconds
Continue? [Y/n] y
proceeding ...
LOCAL_VERSION=1.3.0
DOCKER_IMAGE_VERSION=1.3.0
/home/fabric/fabric-samples/bin/cryptogen

##########################################################
##### Generate certificates using cryptogen tool #########
##########################################################
+ cryptogen generate --config=./crypto-config.yaml
org1.example.com
org2.example.com
+ res=0
+ set +x

/home/fabric/fabric-samples/bin/configtxgen
##########################################################
#########  Generating Orderer Genesis block ##############
##########################################################
+ configtxgen -profile TwoOrgsOrdererGenesis -outputBlock ./channel-artifacts/genesis.block
2018-11-12 18:55:20.241 CST [common/tools/configtxgen] main -> WARN 001 Omitting the channel ID for configtxgen for output operations is deprecated.  Explicitly passing the channel ID will be required in the future, defaulting to 'testchainid'.
2018-11-12 18:55:20.241 CST [common/tools/configtxgen] main -> INFO 002 Loading configuration
2018-11-12 18:55:20.266 CST [common/tools/configtxgen] doOutputBlock -> INFO 003 Generating genesis block
2018-11-12 18:55:20.266 CST [common/tools/configtxgen] doOutputBlock -> INFO 004 Writing genesis block
+ res=0
+ set +x

#################################################################
### Generating channel configuration transaction 'channel.tx' ###
#################################################################
+ configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID mychannel
2018-11-12 18:55:20.302 CST [common/tools/configtxgen] main -> INFO 001 Loading configuration
2018-11-12 18:55:20.325 CST [common/tools/configtxgen] doOutputChannelCreateTx -> INFO 002 Generating new channel configtx
2018-11-12 18:55:20.327 CST [common/tools/configtxgen] doOutputChannelCreateTx -> INFO 003 Writing new channel tx
+ res=0
+ set +x

#################################################################
#######    Generating anchor peer update for Org1MSP   ##########
#################################################################
+ configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID mychannel -asOrg Org1MSP
2018-11-12 18:55:20.362 CST [common/tools/configtxgen] main -> INFO 001 Loading configuration
2018-11-12 18:55:20.385 CST [common/tools/configtxgen] doOutputAnchorPeersUpdate -> INFO 002 Generating anchor peer update
2018-11-12 18:55:20.385 CST [common/tools/configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Writing anchor peer update
+ res=0
+ set +x

#################################################################
#######    Generating anchor peer update for Org2MSP   ##########
#################################################################
+ configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./channel-artifacts/Org2MSPanchors.tx -channelID mychannel -asOrg Org2MSP
2018-11-12 18:55:20.420 CST [common/tools/configtxgen] main -> INFO 001 Loading configuration
2018-11-12 18:55:20.443 CST [common/tools/configtxgen] doOutputAnchorPeersUpdate -> INFO 002 Generating anchor peer update
2018-11-12 18:55:20.443 CST [common/tools/configtxgen] doOutputAnchorPeersUpdate -> INFO 003 Writing anchor peer update
+ res=0
+ set +x

Creating network "net_byfn" with the default driver
Creating volume "net_orderer.example.com" with default driver
Creating volume "net_peer0.org1.example.com" with default driver
Creating volume "net_peer1.org1.example.com" with default driver
Creating volume "net_peer0.org2.example.com" with default driver
Creating volume "net_peer1.org2.example.com" with default driver
Creating peer1.org2.example.com ... done
Creating orderer.example.com    ... done
Creating peer0.org1.example.com ... done
Creating peer1.org1.example.com ... done
Creating peer0.org2.example.com ... done
Creating cli                    ... done

 ____    _____      _      ____    _____
/ ___|  |_   _|    / \    |  _ \  |_   _|
\___ \    | |     / _ \   | |_) |   | |
 ___) |   | |    / ___ \  |  _ <    | |
|____/    |_|   /_/   \_\ |_| \_\   |_|

Build your first network (BYFN) end-to-end test

Channel name : mychannel
Creating channel...
+ peer channel create -o orderer.example.com:7050 -c mychannel -f ./channel-artifacts/channel.tx --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
+ res=0
+ set +x
2018-11-12 10:55:24.154 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:24.193 UTC [cli/common] readBlock -> INFO 002 Received block: 0
===================== Channel 'mychannel' created =====================

Having all peers join the channel...
+ peer channel join -b mychannel.block
+ res=0
+ set +x
2018-11-12 10:55:24.263 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:24.303 UTC [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
===================== peer0.org1 joined channel 'mychannel' =====================

+ peer channel join -b mychannel.block
+ res=0
+ set +x
2018-11-12 10:55:27.378 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:27.423 UTC [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
===================== peer1.org1 joined channel 'mychannel' =====================

+ peer channel join -b mychannel.block
+ res=0
+ set +x
2018-11-12 10:55:30.494 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:30.548 UTC [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
===================== peer0.org2 joined channel 'mychannel' =====================

+ peer channel join -b mychannel.block
+ res=0
+ set +x
2018-11-12 10:55:33.619 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:33.658 UTC [channelCmd] executeJoin -> INFO 002 Successfully submitted proposal to join channel
===================== peer1.org2 joined channel 'mychannel' =====================

Updating anchor peers for org1...
+ peer channel update -o orderer.example.com:7050 -c mychannel -f ./channel-artifacts/Org1MSPanchors.tx --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
+ res=0
+ set +x
2018-11-12 10:55:36.740 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:36.752 UTC [channelCmd] update -> INFO 002 Successfully submitted channel update
===================== Anchor peers updated for org 'Org1MSP' on channel 'mychannel' =====================

Updating anchor peers for org2...
+ peer channel update -o orderer.example.com:7050 -c mychannel -f ./channel-artifacts/Org2MSPanchors.tx --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
+ res=0
+ set +x
2018-11-12 10:55:39.832 UTC [channelCmd] InitCmdFactory -> INFO 001 Endorser and orderer connections initialized
2018-11-12 10:55:39.845 UTC [channelCmd] update -> INFO 002 Successfully submitted channel update
===================== Anchor peers updated for org 'Org2MSP' on channel 'mychannel' =====================

Installing chaincode on peer0.org1...
+ peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/chaincode_example02/java/
+ res=0
+ set +x
2018-11-12 10:55:42.926 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 001 Using default escc
2018-11-12 10:55:42.927 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 002 Using default vscc
2018-11-12 10:55:42.932 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
===================== Chaincode is installed on peer0.org1 =====================

Install chaincode on peer0.org2...
+ peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/chaincode_example02/java/
+ res=0
+ set +x
2018-11-12 10:55:43.008 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 001 Using default escc
2018-11-12 10:55:43.008 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 002 Using default vscc
2018-11-12 10:55:43.015 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
===================== Chaincode is installed on peer0.org2 =====================

Instantiating chaincode on peer0.org2...
+ peer chaincode instantiate -o orderer.example.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc -l java -v 1.0 -c '{"Args":["init","a","100","b","200"]}' -P 'AND ('\''Org1MSP.peer'\'','\''Org2MSP.peer'\'')'
+ res=0
+ set +x
2018-11-12 10:55:43.089 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 001 Using default escc
2018-11-12 10:55:43.089 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 002 Using default vscc
===================== Chaincode is instantiated on peer0.org2 on channel 'mychannel' =====================

Querying chaincode on peer0.org1...
===================== Querying on peer0.org1 on channel 'mychannel'... =====================
+ peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
Attempting to Query peer0.org1 ...3 secs
+ res=0
+ set +x

100
===================== Query successful on peer0.org1 on channel 'mychannel' =====================
Sending invoke transaction on peer0.org1 peer0.org2...
+ peer chaincode invoke -o orderer.example.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["invoke","a","b","10"]}'
+ res=0
+ set +x
2018-11-12 10:56:34.220 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 message:"invoke finished successfully" payload:"a: 90 b: 210"
===================== Invoke transaction successful on peer0.org1 peer0.org2 on channel 'mychannel' =====================

Installing chaincode on peer1.org2...
+ peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/chaincode_example02/java/
+ res=0
+ set +x
2018-11-12 10:56:34.295 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 001 Using default escc
2018-11-12 10:56:34.295 UTC [chaincodeCmd] checkChaincodeCmdParams -> INFO 002 Using default vscc
2018-11-12 10:56:34.302 UTC [chaincodeCmd] install -> INFO 003 Installed remotely response:<status:200 payload:"OK" >
===================== Chaincode is installed on peer1.org2 =====================

Querying chaincode on peer1.org2...
===================== Querying on peer1.org2 on channel 'mychannel'... =====================
+ peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
Attempting to Query peer1.org2 ...3 secs
+ res=0
+ set +x

90
===================== Query successful on peer1.org2 on channel 'mychannel' =====================

========= All GOOD, BYFN execution completed ===========


 _____   _   _   ____
| ____| | \ | | |  _ \
|  _|   |  \| | | | | |
| |___  | |\  | | |_| |
|_____| |_| \_| |____/