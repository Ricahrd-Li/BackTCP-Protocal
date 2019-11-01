import socket
import struct
from ctypes import *
from typing import *

'''
backTcpHeader:
    u_int32_t srcPort;
    u_int32_t recvPort;

    u_int8_t seqNum;
    u_int8_t ackNum;
    
    u_int32_t offset;
    
    u_int8_t winSize;
    u_int8_t reFlag;
'''

class Sender(Structure):
    def __init__(self,winSize=4,srcPort=5005,recvPort=5005,payloadSize=64,bufferSize=512,maxTime=10,recvIp="127.0.0.1"):
        self.recvIp:str = recvIp
        self.recvPort:int = recvPort
        self.srcPort:int = srcPort

        self.payloadSize:int = payloadSize
        self.bufferSize:int = bufferSize
        self.maxTime:int = maxTime
        self.winSize:int = winSize
        self.bufferSizeUsed:int = 0
        self.buffer:bytes = b"" 
        self.seqNum = 0

    def readDataToBuffer(self, f): 
        '''
            Function: read data from file f to sender buffer.
            Param: f is a IO class
        '''
        # when buffer is not full
        if self.bufferSizeUsed + self.payloadSize <= self.bufferSize: 
            data = f.read(64) # read 64 byte
            data = bytes(data)
            self.buffer += data
            self.bufferSizeUsed += 64 # f.read may be smaller than 64!!!!!
            self.seqNum +=1
            return data
        else:
            print("Warning: Buffer is full.")
            return None

    def readBuffer(self):
        if self.bufferSizeUsed > 0:
            data = self.buffer[0:self.payloadSize-1]
            self.bufferSizeUsed = 0 if self.bufferSizeUsed <= 64 else self.bufferSizeUsed - 64
            self.seqNum +=1
            return (data,self.seqNum) 
        else:
            print("Warning: buffer is empty.")
            return None

    def constructHeader(self,seqNum,ackNum,offset,reFlag) -> bytes:
        header = struct.pack("!IIBBIBB", self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)
        return header

    def constructPackage(self,ackNum =0, reFlag=0 ) -> bytes:
        payload , seqNum = self.readBuffer()
        offset = seqNum * 64
        header = self.constructHeader(seqNum,ackNum,offset,reFlag)
        package = header + payload
        return package

    def sendOnePack(self,package):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(package, (self.recvIp, self.recvPort))

    def waitForAck(self):
        pass

    def send(self):
        pass


if __name__ == "__main__":
    sender = Sender()
    with open("/home/richard/计算机网络/BackTCP-Protocal/testdata.txt","rb") as f:
        data1 = sender.readDataToBuffer(f)
        pack1 = sender.constructPackage()
        print(pack1)
        sender.sendOnePack(pack1)

        data2 = sender.readDataToBuffer(f)
        # print(data1)
        # print(data2)

    
