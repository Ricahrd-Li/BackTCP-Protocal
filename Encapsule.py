import struct 

# class backTcpPacket:
#     def __init__(self, srcPort: c_uint8,dstPort,seqNum,ackNum,offset,winSize,reFlag):
#         pass

#     def makeHeader():
def readData(fname,bufferSize, buffer):
    f = open(fname,"rb")
    while (buffer is not full):
        get 64kb data
         


def constructHeader(srcPort, dstPort,seqNum,ackNum,offset,winSize,reFlag):
    header = struct.pack("!BBBBBBB",srcPort, dstPort,seqNum,ackNum,offset,winSize,reFlag)
    return header
    