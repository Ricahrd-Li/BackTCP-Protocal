import socket
import struct

class Receiver:
    def __init__(self,ip="127.0.0.1", port=5005,senderIp="127.0.0.1"):
        self.ip = ip
        self.port = port
        self.senderIp = senderIp

    def constructAckPacket(self,addr,ackNum) -> bytes:
        # let seqnum = 0 and offset = 0
        packet = struct.pack("!IIBBIBB", self.port, addr, 0, ackNum, 0, 0, 0)
        return packet

    def startReceiving(self):
        '''
            Usage: receive the packet from sender and send back ack packet.
        '''
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((self.ip, self.port))   
        print("Reciver: Ready to receive. I am listening...")
        print("=============================================")

        headerSize = struct.calcsize("!IIBBIBB")

        while True:
            # buffer size is 1024 bytes
            rawData, addr = sock.recvfrom(1024)  # addr is a tuple: (ip, port)
            print("## receive packet from", addr,"##")

            srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack("!IIBBIBB",rawData[0:headerSize])
            print("recive header:", srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag)
            print(" ")

            data = rawData[headerSize+1:]
            print("data:", data)
            
            # send ackPacket back
            ackPacket = self.constructAckPacket(addr[1],seqNum) 
            sock.sendto(ackPacket, (self.senderIp, addr[1]))
            print(" ")
            print("Sended ack.")
            print("==========================================")


    

