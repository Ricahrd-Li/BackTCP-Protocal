from sender import *
from sender import Sender

class SharedSendBuffer:
    def __init__ (self, bufferSize = 64):
        self.buffer = b""
        self.bufferSize = bufferSize
        self.bufferSizeUsed = 0

    def __repr__(self):
        return "<shared sender buffer>"

    def addToBuf(self, data, len):
        if self.bufferSizeUsed + len > self.bufferSize:
            print("Wrong! buffer size is not enough")
            return
        else:
            self.bufferSizeUsed +=len
            self.buffer += data

    def removeFromBuf(self,len):
        if self.bufferSizeUsed - len < 0:
            print("Wrong! new bufferSizeUsed is Negtive")
            return           
        else: 
            self.bufferSizeUsed -=len
            self.buffer = self.buffer[:self.bufferSizeUsed-1]
    
    def getBufSizeUsed(self):
        return self.bufferSizeUsed
    

if __name__ == "__main__":
    buffer = SharedSendBuffer()
    sender = Sender()
    


