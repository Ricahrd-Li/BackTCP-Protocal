import socket

class Receiver:
    def __init__(self,ip="",port="5005"):
        self.ip = ip
        self.port = port

    def startUdpServer():
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((ip, port))   
        print("Reciver: Ready to receive. I am listening...")
        while True:
            # buffer size is 1024 bytes
            data, addr = sock.recvfrom(1024) 
            