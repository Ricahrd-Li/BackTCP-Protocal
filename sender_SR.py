import socket
import struct
from ctypes import *
from typing import *
import time
import threading
#import multiprocessing
from signal import signal, SIGTERM
import sys
#from threading import *
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
lock = threading.Lock()
class myTimer(threading.Thread): 
  
    # Thread class with a _stop() method.  
    # The thread itself has to check 
    # regularly for the stopped() condition. 
  
    def __init__(self, sock, item, recvPort=6667, recvIp="127.0.0.1"): 
        self.sock = sock
        self.item = item
        self.recvPort = recvPort
        self.recvIp = recvIp
        self._stop = threading.Event()
        threading.Thread.__init__(self,args=(sock, item, recvPort, recvIp))
  
    # function using _stop function 
    # def stop(self): 
    #     self._stop.set() 
  
    # def stopped(self): 
    #     return self._stop.isSet() 
  
    def run(self): 
        # while True: 
        #     if self.stopped(): 
        #         return
        #     print("Hello, world!") 
        #     time.sleep(1) 
        while True:
            if self._stop.isSet():
                print("thread killed")
                return
            time.sleep(0.01)
            lock.acquire()
            self.sock.sendto(self.item, (self.recvIp, self.recvPort))
            lock.release()

    def join(self, timeout=None):
        """ Stop the thread. """
        self._stop.set()
        #threading.Thread.join(self, timeout)
    
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

        self.lock = threading.Lock()

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

    def isBufferEmpty(self):
        if self.bufferSizeUsed == 0:
            return True
        else:
            return False


    def readBuffer(self):
        ''' Function: read data sender buffer. '''
        
        if self.bufferSizeUsed > 0:
            data = self.buffer[0:self.payloadSize+1] # a queue
            self.buffer = self.buffer[self.payloadSize+1:] 
            if self.bufferSizeUsed <= 64 :
                self.bufferSizeUsed = 0 
            else:
                self.bufferSizeUsed =  self.bufferSizeUsed - 64
            return data 
        else:
            print("Warning: buffer is empty.")
            return None

    def constructHeader(self,seqNum,ackNum,offset,reFlag) -> bytes:
        '''
            Function: construct header. 
        '''
        header = struct.pack(form, self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)
        return header

    def constructPackage(self,seqNum, payload = None, ackNum =0, reFlag=0 ) -> bytes:
        '''
            Function: constuct package
            Note: inside this function I call self.readBuffer(), so no need to call self.readBuffer() outside this function!
        '''
        if payload == None:
            payload = self.readBuffer()
            if payload == None:
                return (None,None)
        offset = seqNum * 64
        header = self.constructHeader(seqNum,ackNum,offset,reFlag)
        package = header + payload
        return package


    def sendOnePack(self,f):
        '''
            This function is used to debug.
            Param: f is an IO class
        '''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            self.readDataToBuffer(f)
            pkt, data = self.constructPackage(seqNum=1)
            sock.sendto(pkt, (self.recvIp, self.recvPort))
            print(data)
    
    # def reSend(self,sock,item,stop):
    #     while True:
    #         if stop():
    #             print("thread killed")
    #             break
    #         time.sleep(0.01)
    #         self.lock.acquire()
    #         sock.sendto(item, (self.recvIp, self.recvPort))
    #         self.lock.release()
            

    def SendSR(self,f):

        headerSize = struct.calcsize(form)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

            sock.bind((self.ip, self.srcPort))
            baseSeq = 1
            nextSeq = baseSeq
            N = self.winSize            
            timerList = []
            recvWin = []
            # 初始1,2,3,4四个包存入发送队列
            self.readDataToBuffer(f)
            sock.setblocking(0)
            while True:
                while nextSeq < baseSeq + N:
                    print("ns:",nextSeq)
                    pkt = self.constructPackage(seqNum = nextSeq)
                    if pkt == None:
                        return
                    lock.acquire()
                    sock.sendto(pkt, (self.recvIp, self.recvPort))
                    lock.release()
                    #timer = threading.Thread(target=self.reSend, args=(sock,pkt))
                    timer = myTimer(sock=sock, item=pkt)
                    timer.start()
                    timerList.append(timer)
                    recvWin.append(0)
                    nextSeq += 1
                while nextSeq == baseSeq + N:
                    #print(len(multiprocessing.active_children()))
                    #print(threading.active_count())
                    data = None
                    try:
                        data, addr = sock.recvfrom(1024)
                    except BlockingIOError:
                        pass
                    if data!= None:
                        srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(form,data[0: headerSize  ])
                        print("ack: " , ackNum)
                        if ackNum in list(range(baseSeq,baseSeq+N)):
                            recvWin[ackNum-baseSeq] = 1
                        i = 0
                        print(recvWin)
                        while i<len(recvWin) and recvWin[i] == 1:
                            #timerList[i].terminate()
                            #time.sleep(0.01)
                            # if not timerList[i].is_alive():
                            #     timerList[i].join()
                            timerList[i].join()
                            i += 1
                            baseSeq += 1
                            print(baseSeq)
                            #print(timerList)
                        timerList = timerList[i:]
                        recvWin = recvWin[i:]
                self.readDataToBuffer(f)
if __name__ == "__main__":
    sender = Sender()
    with open("input.bin","rb") as f:
        sender.SendSR(f)

    
