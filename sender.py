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

form = "!IIIIIBB"  # 指示报头打包的格式
 
class Sender(Structure):
    def __init__(self, winSize=4, srcPort=8000, recvPort=6667, payloadSize=64, bufferSize=512, maxTime=10,srcIp = "127.0.0.1", recvIp="127.0.0.1"):
        self.recvIp:str = recvIp
        self.recvPort:int = recvPort
        self.srcPort:int = srcPort
        self.ip = srcIp

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
            # print("Warning: Buffer is full.")
            return None

    def readBuffer(self):
        ''' Function: read data sender buffer. '''
        
        if self.bufferSizeUsed > 0:
            data = self.buffer[0:self.payloadSize+1] # a queue
            # print(data)
            self.buffer = self.buffer[self.payloadSize+1:] 
            if self.bufferSizeUsed <= 64 :
                self.bufferSizeUsed = 0 
            else:
                self.bufferSizeUsed =  self.bufferSizeUsed - 64
            # print(self.bufferSizeUsed)
            return data 
        else:
            # print("Warning: buffer is empty.")
            return None

    def constructHeader(self,seqNum,ackNum,offset,reFlag) -> bytes:
        '''
            Function: construct header. 
            Param: 
        '''
        header = struct.pack(form, self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)
        return header

    def constructPackage(self,seqNum, payload = None, ackNum =0, reFlag=0 ) -> bytes:
        if payload == None:
            payload = self.readBuffer()
        offset = seqNum * 64
        header = self.constructHeader(seqNum,ackNum,offset,reFlag)
        package = header + payload
        return (package, payload)


    def send(self,f):

        def startTimer(timer):
            timer = time.time()
            return timer

        def isTimeOut(timer):
            if timer == 0: # timer is stopped
                return False
            if time.time() - timer > 0.01 :
                return True
            else:
                return False

        def stopTimer(timer):
            timer = 0
            return timer
        
        headerSize = struct.calcsize(form)
        # print(headerSize)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.ip, self.srcPort))
            baseSeq = 1
            nextSeq = baseSeq
            N = self.winSize
            timer = 0
            
            pktList = []

            while self.readDataToBuffer(f) !=0:
                # 初始发包
                while nextSeq < baseSeq + N:
                    pkt,payload = self.constructPackage(seqNum = nextSeq)
                    pktList.append((payload,nextSeq)) # save pkt 
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
                        # print(data)
                        srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(form,data[0: headerSize  ])
                        # print(srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag)
                        print("ack: " , ackNum)
                        if ackNum >= baseSeq:
                            pktList = pktList[ackNum - baseSeq :]
                            baseSeq = ackNum + 1 
                            if baseSeq == nextSeq:
                                timer = stopTimer(timer)
                                break # go to next window 
                            else:
                                timer = startTimer(timer)
                
                # 超时重传
                if isTimeOut(timer):
                    # print("time out.")
                    timer = stopTimer(timer)
                    for i in range(nextSeq - baseSeq):
                        pkt,_ = self.constructPackage(payload = pktList[i][0], seqNum =pktList[i][1], reFlag = 1 )
                        sock.sendto(pkt, (self.recvIp, self.recvPort))

                    timer = startTimer(timer)
                    continue
                    
            print("transfer finished.")

    def sendOnePack(self,f):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            self.readDataToBuffer(f)
            pkt, data = self.constructPackage(seqNum=1)
            sock.sendto(pkt, (self.recvIp, self.recvPort))
            print(data)


if __name__ == "__main__":
    sender = Sender()
    with open("testdata.txt","rb") as f:
        # data1 = sender.readDataToBuffer(f)
        sender.send(f)
        # sender.sendOnePack(f)
        # sender.sendOnePack(f)
        # sender.sendOnePack(f)
        # pack1 = sender.constructPackage()
        # print(pack1)
        # sender.sendOnePack(pack1,sender.seqNum)
        # print(sender.seqNum)
        # sender.waitForAck(sender.seqNum)
        # data2 = sender.readDataToBuffer(f)
        # print(data1)
        # print(data2)

    
