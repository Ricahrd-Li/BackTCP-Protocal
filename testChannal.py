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
                        mode = random.randint(1,10)
                        if mode <= 6: # 正常发送
                            print("正常")
                            sock.sendto(rawData, (self.ip,self.outPort))    
                        
                        elif mode <= 8: # 直接丢包
                            print("丢包。")
                            continue 
                        
                        else: # 序号变
                            pass
                    
                    else: # 是从receiver发来的ack包
                        mode = random.randint(1,10)
                        if mode <= 10: # 正常发送
                            print("ack正常")
                            sock.sendto(rawData, (self.ip,self.senderPort))
                        
                        elif mode <= 8: # 直接丢包
                            print("ack丢包。")
                            continue 
                        
                        else: # 序号变
                            pass
if __name__ == "__main__":
    testChannal =  Channal()
    testChannal.run()