import socket
import struct
from ctypes import *

class Sender(Structure):
    def __init__(self,srcPort,winSize,payloadSize=64,bufferSize=512,maxTime=10,recvIp="127.0.0.1",recvPort="5005"):
        self.recvIp:str = recvIp
        self.recvPort:int = recvPort
        self.payloadSize:int = payloadSize
        self.bufferSize:int = bufferSize
        self.maxTime:int = maxTime
        self.srcPort:int = srcPort
        self.winSize:int = winSize
        self.bufferSizeUsed:int = 0
        self.buffer:bytes = b"" 

    def readDataToBuffer(self,f):
        '''Function: read data from file to sender buffer.'''

        if self.bufferSizeUsed + self.payloadSize <= self.bufferSize: # buffer is not full
            data = f.read(self.payloadSize) # read 64 bytes
            self.buffer = self.buffer + data
            return data
        else:
            print("Warning: Buffer is full.")
            return None

    def readBuffer(self):
        if self.bufferSizeUsed > 0:
            data = self.buffer[0,self.payloadSize-1]
            self.bufferSizeUsed = 0 if self.bufferSizeUsed <= 64 else self.bufferSizeUsed - 64
            return data 
        else:
            print("Warning: buffer is empty.")
            return None

    def constructHeader(self,seqNum,ackNum,offset,reFlag) -> bytes:
        header = struct.pack("B"*7, self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)
        return header

    def constructPackage(self,seqNum,ackNum,offset,reFlag,fname) -> bytes:
        header = constructHeader(seqNum,ackNum,offset,reFlag)
        payload = readBuffer()
        package = header + payload
        return package

    def send(self,package):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(package, (self.recvIp, self.recvPort))

    def pipelineSend(self,fname):
        with open(fname,"rb") as f:
            readDataToBuffer(f)

        pass


    
