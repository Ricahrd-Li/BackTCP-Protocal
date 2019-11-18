import random
import socket
import struct

class Channal:
    def __init__(self,ip = "127.0.0.1",inPort = 6667 , outPort = 6666, senderPort = 8000):
        self.ip = ip
        self.inPort = inPort
        self.outPort = outPort
        self.form = "!IIIIIBB"
        self.headerSize = struct.calcsize(self.form)
        self.senderPort = senderPort

        self.pktBuffer = []
        self.ackBuffer = []

    def run(self):
        senderAddr = 0

        print("Test Channal is running.")
        print("===============================================")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.ip, self.inPort))
            sock.setblocking(0)
            while True:
                rawData = None
                try:
                    rawData, addr = sock.recvfrom(1024)  # addr is a tuple: (ip, port)
                except BlockingIOError:
                    continue

                if rawData != None:
                    srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(self.form,rawData[0:self.headerSize])
                
                    if seqNum != 0: # 是从sender发来的包
                        if reFlag == 1: #如果是重传的数据包，经过测试信道不会丢包。
                            print("正常")
                            sock.sendto(rawData, (self.ip,self.outPort))    
                            continue
                        else:
                            mode = random.randint(1,10)
                            if mode <= 5: # 正常发送
                                print("正常")
                                sock.sendto(rawData, (self.ip,self.outPort))    
                            
                            elif mode <= 8: # 直接丢包
                                print("丢包。")
                                continue 
                            
                            else: # 序号变
                                print("失序")
                                # 当buffer中有1个包时：交换顺序发送达到失序目的
                                if len(self.pktBuffer) == 1:
                                    sock.sendto(self.pktBuffer[0], (self.ip,self.outPort))
                                    sock.sendto(rawData, (self.ip,self.outPort))
                                    self.pktBuffer = []
                                else:
                                    self.pktBuffer.append(rawData)
                    
                    else: # 是从receiver发来的ack包
                        mode = random.randint(1,10)
                        if mode <= 10: # 正常发送
                            print("ack正常")
                            sock.sendto(rawData, (self.ip,self.senderPort))
                        
                        elif mode <= 8: # 直接丢包
                            print("ack丢包。")
                            continue 
                        
                        else: # 序号变
                            print("ack失序")
                            if len(self.ackBuffer) == 1:
                                sock.sendto(self.ackBuffer[0], (self.ip,self.outPort))
                                sock.sendto(rawData, (self.ip,self.outPort))
                                self.ackBuffer = []
                            else:
                                self.ackBuffer.append(rawData)
if __name__ == "__main__":
    testChannal =  Channal()
    testChannal.run()