import socket
import struct
from ctypes import *
from typing import *
import time
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
    def __init__(self, winSize=4, srcPort=8000, recvPort=5005, payloadSize=64, bufferSize=512, maxTime=10, recvIp="127.0.0.1"):
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
        if self.bufferSizeUsed < self.bufferSize: 
            data = f.read(self.bufferSize - self.bufferSizeUsed) 
            data = bytes(data)
            self.buffer += data
            self.bufferSizeUsed += len(data) 
            return len(data)
        else:
            print("Warning: Buffer is full.")
            return None

    def readBuffer(self):
        if self.bufferSizeUsed > 0:
            data = self.buffer[0:self.payloadSize-1] # a queue
            self.buffer = self.buffer[self.payloadSize:] 
            if self.bufferSizeUsed <= 64 :
                self.bufferSizeUsed = 0 
            else:
                self.bufferSizeUsed =  self.bufferSizeUsed - 64
            return data 
        else:
            print("Warning: buffer is empty.")
            return None

    def constructHeader(self,seqNum,ackNum,offset,reFlag) -> bytes:
        header = struct.pack("!IIIBIBB", self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)
        return header

    def constructPackage(self,seqNum, ackNum =0, reFlag=0 ) -> bytes:
        payload = self.readBuffer()
        offset = seqNum * 64
        header = self.constructHeader(seqNum,ackNum,offset,reFlag)
        package = header + payload
        return package

    def send(self,f):

        def startTimer(timer):
            timer = time.time()
            return timer

        def isTimeOut(timer):
            if time.time() - timer > 0.01 :
                return True
            else:
                return False

        def stopTimer(timer):
            timer = 0
            return timer
        
        headerSize = struct.calcsize("!IIIBIBB")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            baseSeq = 1
            nextSeq = baseSeq
            N = self.winSize
            timer = 0
            
            pktList = []

            while self.readDataToBuffer(f) !=0:
                # 初始发包
                while nextSeq < baseSeq + N:
                    pkt = self.constructPackage(seqNum = nextSeq)
                    pktList.append(pkt) # save pkt 
                    sock.sendto(pkt, (self.recvIp, self.recvPort))
                    if baseSeq == nextSeq:
                        timer = startTimer(timer) 
                    nextSeq += 1 

                # 接收ack 与重传
                sock.setblocking(0)
                while not isTimeOut(timer):
                    data = None
                    try:
                        data, addr = sock.recvfrom(1024)
                    except BlockingIOError:
                        pass
                    if data != None:
                        srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack("!IIIBIBB",data[0:headerSize])
                        print(srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag)
                        if ackNum > baseSeq:
                            pktList = pktList[ackNum - baseSeq :]
                            baseSeq = ackNum + 1 
                            if baseSeq == nextSeq:
                                timer = stopTimer(timer)
                                break # go to next window 
                            else:
                                timer = startTimer(timer)
                # 超时重传
                if isTimeOut(timer):
                    for i in range(nextSeq - baseSeq):
                        sock.sendto(pktList[i], (self.recvIp, self.recvPort))
                    continue
                    
            print("transfer finished.")

    # def waitForAck(self,sequenceNum):
    #     headerSize = struct.calcsize("!IIBBIBB")
    #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    #         data, addr = sock.recvfrom(1024)
    #         print(data)
    #         srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack("!IIBBIBB",data[0:headerSize])
    #         print(srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag)
    #         if ackNum == sequenceNum:
    #             return 1
    #         else:
    #             return 0


if __name__ == "__main__":
    sender = Sender()
    with open("/home/richard/计算机网络/BackTCP-Protocal/testdata.txt","rb") as f:
        # data1 = sender.readDataToBuffer(f)
        sender.send(f)
        # pack1 = sender.constructPackage()
        # print(pack1)
        # sender.sendOnePack(pack1,sender.seqNum)
        # print(sender.seqNum)
        # sender.waitForAck(sender.seqNum)
        # data2 = sender.readDataToBuffer(f)
        # print(data1)
        # print(data2)

    
