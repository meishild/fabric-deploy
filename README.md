# fabric生产部署快速脚本
v 0.0.1

## 生成配置
* python环境依赖python3+jinja2

```
python3 build.py
```
* 如果需要清理生成的配置，完全重新生成使用,`python3 build.py clean`

## 将生成的machine目录复制到对应的机器下。
所有的配置都依赖config.py，最好只修改ip以及对应的机器，现阶段只支持分布式部署，单机内尽量不要部署相同应用未测试通过。

## 最终部署测试结果
* 192.168.12.74 zookeeper1 kafka1 orderer1
* 192.168.12.75 zookeeper2 kafka2 orderer2
* 192.168.12.76 zookeeper3 kafka3 org0.peer0
* 192.168.12.77 kafka4 org0.peer1 explorer
* 192.168.12.78 org1.peer0

## test
### clean
docker stop $(docker ps -q) 
docker rm $(docker ps -aq) && rm -fr /opt/chainData/ && docker network rm net

### cp
cd /home/fabric/ && rm -fr machine* && rm -fr /home/songhaiyang/machine*

rm -fr machine.tar.gz && scp songhaiyang@192.168.12.79:/home/fabric/fabric-deploy/machine.tar.gz ./

scp machine.tar.gz songhaiyang@192.168.12.74: && scp machine.tar.gz songhaiyang@192.168.12.75: && scp machine.tar.gz songhaiyang@192.168.12.76: && scp machine.tar.gz songhaiyang@192.168.12.77: && scp machine.tar.gz songhaiyang@192.168.12.78:

cd /home/fabric && mv /home/songhaiyang/machine.tar.gz /home/fabric && tar zxvf machine.tar.gz


### 74
cd /home/fabric/machine/orderer/192.168.12.74/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d

### 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d

### 76
cd /home/fabric/machine/orderer/192.168.12.76/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d

### 77
cd /home/fabric/machine/orderer/192.168.12.77/ && docker-compose -f docker-kafka.yaml up -d

===================== ZOOKEPPER & KAFKA Start Finish ===================== 
### 74
docker exec -it z1 bin/zkServer.sh status

cd /home/fabric/machine/orderer/192.168.12.74/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer1.shuwen.com

### 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer2.shuwen.com 

===================== ORDERER Start Finish ===================== 

### 76
cd /home/fabric/machine/org1/192.168.12.76/ && sh scripts/initCouchDB.sh
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d
docker-compose -f docker-compose-ca.yaml up -d

===================== peer0.org1 PEER AND CA Start Finish ===================== 

### 77
cd /home/fabric/machine/org1/192.168.12.77/ && sh scripts/initCouchDB.sh
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d
docker logs -f peer1.org1.icdoit.com
===================== peer1.org1 PEER Start Finish ===================== 


### 78
cd /home/fabric/machine/org2/192.168.12.78/ && sh scripts/initCouchDB.sh
docker-compose -f docker-compose-couchdb.yaml -f docker-compose-peer.yaml -f docker-compose-cli.yaml up -d

===================== peer0.org2 PEER Start Finish ===================== 

### 76
docker exec cli peer channel create -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/channel.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem

===================== Channel 'mychannel' created =====================

docker exec cli cp mychannel.block scripts
docker exec cli peer channel join -b mychannel.block
docker exec cli peer channel list

===================== peer0.org1 joined channel 'mychannel' =====================

####
scp songhaiyang@192.168.12.76:/home/fabric/machine/org1/192.168.12.76/scripts/mychannel.block ./
scp mychannel.block songhaiyang@192.168.12.77: && scp mychannel.block songhaiyang@192.168.12.78:

===================== peer1.org1 joined channel 'mychannel' =====================

### 77
cp /home/songhaiyang/mychannel.block /home/fabric/machine/org1/192.168.12.77/scripts
docker exec cli peer channel join -b scripts/mychannel.block

===================== peer0.org2 joined channel 'mychannel' =====================
### 78
cp /home/songhaiyang/mychannel.block /home/fabric/machine/org2/192.168.12.78/scripts
docker exec cli peer channel join -b scripts/mychannel.block

===================== peer1.org1 joined channel 'mychannel' =====================


### 76
docker exec cli peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org1MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem

===================== Anchor peers updated for org 'Org1MSP' on channel 'mychannel' =====================

### 78
docker exec -it cli peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org2MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem

===================== Anchor peers updated for org 'Org2MSP' on channel 'mychannel' =====================


### 76
docker exec -it cli peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
===================== Chaincode is installed on peer0.org1 =====================

### 77
docker exec -it cli peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
===================== Chaincode is installed on peer0.org1 =====================

### 78
docker exec -it cli peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
docker exec -it cli peer chaincode instantiate -o orderer1.shuwen.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem -C mychannel -n mycc -l java -v 1.0 -c '{"Args":["init","a","100","b","200"]}'  -P 'OR ('\''Org1MSP.peer'\'','\''Org2MSP.peer'\'')'
docker exec -it cli peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
===================== Chaincode is instantiated on peer0.org1 on channel 'mychannel' =====================

### 76
docker exec -it cli peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
===================== Chaincode is installed on peer0.org2 =====================

### 74
cd /home/fabric/machine/org1/192.168.12.74/explorer
docker-compose -f docker-compose-explorer-postgres.yaml up -d

docker exec fabric-explorer-db  /bin/bash /opt/createdb.sh

docker-compose -f docker-compose-explorer.yaml up