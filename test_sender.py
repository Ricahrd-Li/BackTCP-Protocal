import unittest
from ctypes import *
import sys

from sender import Sender

class Interger(Structure):
    _fields_ =[ ("a", c_uint)]

if __name__ == "__main__":
    backTcpSender = Sender(winSize = 4)
    data = backTcpSender.readDataToBuffer("/home/richard/计算机网络/BackTCP-Protocal/testdata.txt")
    # interger = Interger(1)
    # print(sys.getsizeof(interger.a))
   
    # print(data)
    # print(sys.getsizeof(data))
    header = backTcpSender.constructHeader(1,1,1,1)
    print(header)
    print(sys.getsizeof(header))




