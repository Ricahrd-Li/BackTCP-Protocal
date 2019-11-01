import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = "<!DOCTYPE html><h1>Hello, World!<\h1>"

MESSAGE = bytes(MESSAGE,encoding="utf-8")

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
print("Already sent.")