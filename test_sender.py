import unittest

import sys

from sender import Sender

if __name__ == "__main__":
    backTcpSender = Sender(srcPort = "127.0.0.1",winSize = 4)

    data = backTcpSender.readDataToBuffer("testdata.txt")
    print(data)
    print(sys.getsizeof(data))
    # print(backTcpSender.readDataToBuffer("testdata.txt"))





