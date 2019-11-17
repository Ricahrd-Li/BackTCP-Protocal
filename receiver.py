import socket
import struct
import datetime

form = "!IIIIIBB"

class Receiver:
    def __init__(self,ip="127.0.0.1", port=6666,senderIp="127.0.0.1"):
        self.ip = ip
        self.port = port
        self.senderIp = senderIp

    def constructAckPacket(self,addr,ackNum) -> bytes:
        # let seqnum = 0 and offset = 0
        packet = struct.pack(form, self.port, addr, 0, ackNum, 0, 0, 0)
        return packet

    def startReceiving(self):
        '''
            Usage: receive the packet from sender and send back ack packet.
        '''
        f = open("recv_data","wb")
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((self.ip, self.port))
        sock.settimeout(0.1)   
        print("Reciver: Ready to receive. I am listening...")
        print("=============================================")

        headerSize = struct.calcsize(form)
        recvBase = 0
        recvBuffer = b""
        while True:
            # time = datetime.now()
            # buffer size is 1024 bytes
            rawData = None
            try:
                rawData, addr = sock.recvfrom(1024)  # addr is a tuple: (ip, port)
            except socket.timeout:
                f.write(recvBuffer)
                recvBuffer = b""
                continue
            # print("## receive packet from", addr,"##")

            srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(form,rawData[0:headerSize])
            data = rawData[headerSize:]
            # if reFlag == 0 :
                # print("recive header:", srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag)
            print("recive seq:",  seqNum)
            print(" ")
            if seqNum != recvBase + 1:
                ackPacket = self.constructAckPacket(addr[1],recvBase)
                sock.sendto(ackPacket, (self.senderIp, addr[1]))
                # print(data)
                print(" ")
                print("Sended ack：", recvBase)
                print("==========================================")
                continue
            else:
                print("data:", data)
                # f.write(data)
                recvBuffer +=data
                recvBase +=1
                # send ackPacket back
                ackPacket = self.constructAckPacket(addr[1],recvBase) 
                sock.sendto(ackPacket, (self.senderIp, addr[1]))
                print(" ")
                print("Sended ack.")
                print("==========================================")
            # if reFlag == 1:



if __name__ == "__main__":
    ''' Test buffer '''
    receiver = Receiver()
    receiver.startReceiving()