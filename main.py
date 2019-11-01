from sender import *

class SharedSendBuffer:
    def __init__ (self, bufferSize = 64):
        self.buffer = b""
        self.bufferSize = bufferSize
        self.bufferSizeUsed = 0

    def __repr__(self):
        return "<shared sender buffer>"

    def addToBuf(self, data, len):
        try:
            self.bufferSizeUsed +=len
            self.buffer += data
        except self.bufferSizeUsed > self.bufferSize:
            print("Wrong! buffer size is not enough")

    def removeFromBuf(self,len):
        try: 
            self.bufferSizeUsed -=len
            self.buffer = self.buffer[:self.bufferSizeUsed-1]
        except IndexError:
            print("Wrong! new bufferSizeUsed is Negtive")
    
    def getBufSizeUsed(self):
        return self.bufferSizeUsed
    

if __name__ == "__main__":
    buffer = SharedSendBuffer()


