import socket 

UDP_IP = ""
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
print("I am listening...")
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # reply = 'OK...' + data.decode("utf-8")
    # reply = reply.encode("utf-8")
    # sock.sendto(reply , addr)
    print ("received message:", str(data))