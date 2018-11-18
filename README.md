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

docker logs -f k1

## 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d

## 76
cd /home/fabric/machine/orderer/192.168.12.76/ && docker-compose -f docker-zk.yaml -f docker-kafka.yaml up -d

## 77
cd /home/fabric/machine/orderer/192.168.12.77/ && docker-compose -f docker-kafka.yaml up -d

===================== ZOOKEPPER & KAFKA Start Finish ===================== 

## 74
cd /home/fabric/machine/orderer/192.168.12.74/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer1.shuwen.com

## 75
cd /home/fabric/machine/orderer/192.168.12.75/ && docker-compose -f docker-compose-orderer.yaml up -d && docker logs -f orderer1.shuwen.com

===================== ORDERER Start Finish ===================== 

## 76
cd /home/fabric/machine/org1/192.168.12.76/ && sh scripts/initPeer.sh && docker-compose -f docker-compose-peer.yaml up -d

docker-compose -f docker-compose-ca.yaml up -d

===================== peer0.org1 PEER AND CA Start Finish ===================== 

## 77
cd /home/fabric/machine/org1/192.168.12.77/ && sh scripts/initPeer.sh && docker-compose -f docker-compose-peer.yaml up -d
===================== peer1.org1 PEER Start Finish ===================== 


## 78
cd /home/fabric/machine/org2/192.168.12.78/ && sh scripts/initPeer.sh && docker-compose -f docker-compose-peer.yaml up -d
===================== peer0.org2 PEER Start Finish ===================== 

# 76
docker exec -it cli bash

peer channel create -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/channel.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem
===================== Channel 'mychannel' created =====================

cp mychannel.block scripts 
peer channel join -b mychannel.block
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
peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org1MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem

===================== Anchor peers updated for org 'Org1MSP' on channel 'mychannel' =====================

# 77
peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
===================== Chaincode is installed on peer0.org1 =====================


peer chaincode instantiate -o orderer1.shuwen.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem -C mychannel -n mycc -l java -v 1.0 -c '{"Args":["init","a","100","b","200"]}'  -P 'OR ('\''Org1MSP.peer'\'','\''Org2MSP.peer'\'')'
===================== Chaincode is instantiated on peer0.org1 on channel 'mychannel' =====================

peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'

# 78
peer channel update -o orderer1.shuwen.com:7050 -c mychannel -f ./channel-artifacts/Org2MSPanchors.tx --tls true --cafile=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/shuwen.com/tlsca/tlsca.shuwen.com-cert.pem
===================== Anchor peers updated for org 'Org2MSP' on channel 'mychannel' =====================

peer chaincode install -n mycc -v 1.0 -l java -p /opt/gopath/src/github.com/chaincode/java/
peer chaincode query -C mychannel -n mycc -c '{"Args":["query","a"]}'
===================== Chaincode is installed on peer0.org2 =====================

