import unittest

from main import SharedSendBuffer
from receiver import Receiver

def testBuffer():
    buffer = SharedSendBuffer()
    data1 = b"asdasdddddddddddasdasdasfasfasdasdasdasdddddddddddasdasdasfasfasdasdasdasdddddddddddasdasdasfasfasdasd"
    data2 = b"asdsad"
    # print(len(data1))
    # print(len(data2))
    buffer.addToBuf(data1,len(data1))
    print(buffer.buffer)
    buffer.addToBuf(data2,len(data2))
    print(buffer.buffer)
    buffer.removeFromBuf(len(data1))
    print(buffer.buffer)
    buffer.removeFromBuf(2)
    print(buffer.buffer)

def testReceiver():
    receiver = Receiver()
    receiver.startReceiving()

if __name__ == "__main__":
    ''' Test buffer '''
    # testBuffer()
    testReceiver()


