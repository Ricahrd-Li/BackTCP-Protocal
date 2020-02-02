# 计算机网络课程作业报告：实现简单可靠的传输层协议 backTCP
### Zhehao Li

## 1.实验内容
实现一个可靠传输协议 backTCP, 实现面向无连接的可靠传输功能,能够解决数据包在传输过程中出现的乱序以及丢包问题。并实现Ｇo-back-N 和 SR 两种传输方式。

说明:假设一个待传送的文件,按照”字节-空格-字节”的方式存储,其中每个
字节由一个十六进制数表示,例如,0A 49 4A 49 4A 49 4A 49 4A 49 4A 41 4A 41
4C ......, 
+ 首先,将这个文件读入,然后通过编写的数据包封装函数,将文件按照
backTCP 数据报结构进行封装; 
+ 封装后,使用滑动窗口协议进行按序发送,每
个包调用一次套接字 TCP 发送函数,发送到我们提供的测试信道中; 
+ 测试信道处理后,会使用 TCP 发送到接收端程序中,接收端程序确定收到的数据报序
号,并确定哪些数据包在传输过程中被丢弃; 对第一个丢弃的包序号前面正确
收到的分组进行确认(确认帧通过 TCP 直接发送到发送端),之后,发送端重
传序号后面所有的帧,例如,发送了 1,2,3,4,5 这几个数据包,其中 4 丢
包了,对 3 进行确认,发送端重传 4 和 5 两个数据包。
+ 为了简化处理,我们在
数据包头部加了一个 flag 字段,指示是否为重传的数据包,1 表示重传。重传
的数据包经过测试信道不会丢包。


## 2.实验环境
Ubuntu 17.10, Vscode，Python 3.6

## 3.实现步骤

我采用的socket连接均为UDP连接。

1. 测试信道

    我实现了一个简单但是功能完善的测试信道，可以实现正常传输、丢包以及失序传输。
    使用产生随机数的方式决定每次对信道中的报文采取三种中的一种。

    发送端发送数据时：Sender发送至6667端口，Receiver从6666端口接受报文。 \
    接收方发送ack报文时：Receiver发送至6666端口，Sender从6667端口收ack报文。

    ```python
    class Channal:
    def __init__(self,ip = "127.0.0.1",inPort = 6667 , outPort = 6666, senderPort = 8000):
 
    ```
    a. 正常传输：
    ```python
    if seqNum != 0: # 是从sender发来的包
            if reFlag == 1: #如果是重传的数据包，经过测试信道不会丢包。
                print("正常")
                sock.sendto(rawData, (self.ip,self.outPort))    
                continue
            else:
                mode = random.randint(1,10)
                if mode <= 5: # 正常发送
                    print("正常")
                    sock.sendto(rawData, (self.ip,self.outPort))    
    ```

    b.丢包：
    ```python            
                elif mode <= 8: # 直接丢包
                    print("丢包。")
                    continue 
    ```
    c. 失序：使用一个buffer缓存之前一个报文，然后颠倒顺序发送
    ```python
                else: # 序号变
                    print("失序")
                    # 当buffer中有1个包时：交换顺序发送达到失序目的
                    if len(self.pktBuffer) == 1:
                        sock.sendto(self.pktBuffer[0], (self.ip,self.outPort))
                        sock.sendto(rawData, (self.ip,self.outPort))
                        self.pktBuffer = []
                    else:
                        self.pktBuffer.append(rawData)
    ```

2. 发送端 \
实现``Sender``类 \
    a. Sender使用的端口是8000
    ```python
    class Sender(Structure):
        def __init__(self, winSize=4, srcPort=8000, recvPort=6667, payloadSize=64, bufferSize=512, maxTime=10,srcIp = "127.0.0.1", recvIp="127.0.0.1"):
    ```
    b.在Sender类内部设置发送buffer，有从文件读数据入buffer以及从buffer读数据两个函数。

    ```python
        def readDataToBuffer(self, f)
    ```
    ```python
        def readBuffer(self)
    ```
    c. 数据包的组装方式
    报头的组装使用``struct``库内的``pack``函数。
    ```python

    header = struct.pack(form, self.srcPort, self.recvPort, seqNum, ackNum, offset, self.winSize, reFlag)

    ```
    解包可以使用``unpack``函数。
    ```
    srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(form,data[0: headerSize  ])

    ```

    d.Go-Back-N 发送方式：\
    使用一个长度大小与发送窗口大小相同的发送队列``pktQueue``\
    核心方法是：每收到一个有效的ackNum (ackNum > baseSeq)就将已经确认接收的数据包从``pktQueue``出队，并补充新的数据包。\
    外层``While``中每次发送都发送整个pktQueue中所有数据包。
    ```python
     def SendGoBackN(self,f):

        ...

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.ip, self.srcPort))

            baseSeq = 1
            nextSeq = baseSeq
            N = self.winSize
            timer = 0
            pktQueue = []

            # 初始1,2,3,4四个包存入发送队列
            self.readDataToBuffer(f)
            while nextSeq < baseSeq + N:
                pkt,payload = self.constructPackage(seqNum = nextSeq)
                pktQueue.append((pkt, payload,nextSeq)) # 数据报入队

                nextSeq += 1 
            
            # 若队列不为空，说明发送还没有结束
            while len(pktQueue)!= 0: 

                # 发送包队列里面的包，并设置一个初始定时器
                timer = startTimer(timer)
                for item in pktQueue:
                    sock.sendto(item[0], (self.recvIp, self.recvPort))
   ```

    内层``while``循环实现的是定时器未超时时接收ack、移动发送窗口(通过``pktQueue``出队入队实现)的逻辑
   ```python                 
                # 接收ack 与重传
                sock.setblocking(0)
                while not isTimeOut(timer):
                    data = None
                    try:
                        data, addr = sock.recvfrom(1024)
                    except BlockingIOError:
                        pass

                    # 接受ack
                    if data != None:
                        srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag =\
                             struct.unpack(form,data[0: headerSize  ])
                        print("ack: " , ackNum)
                        if ackNum >= baseSeq:
                            pktQueue = pktQueue[ackNum - baseSeq + 1 :]
                            baseSeq = ackNum + 1

                            # 刷新 timer
                            timer = startTimer(timer)
                            # pktQueue 操作
                            while nextSeq < baseSeq + N:
                                pkt,payload = self.constructPackage(seqNum = nextSeq)
                                if pkt == None:
                                    print("tranfer finish!")
                                    return
                                pktQueue.append((pkt, payload,nextSeq)) # save pkt 
                                nextSeq += 1 

                self.readDataToBuffer(f)
            print("transfer finished.")
    ```


3. go-back-N 接收端
    实现了接收缓存以及发送ack的逻辑

    ```python
        while True:
            rawData = None
            try:
                rawData, addr = sock.recvfrom(1024)  # addr is a tuple: (ip, port)
            except socket.timeout:
                f.write(recvBuffer)
                recvBuffer = b""
                continue
            
            # 解包
            srcPort, recvPort, seqNum, ackNum, offset, winSize, reFlag = struct.unpack(form,rawData[0:headerSize])
            data = rawData[headerSize:]
            print("recive seq:",  seqNum)
            print(" ")
            # 不是期待的seqNum
            if seqNum != recvBase + 1:
                ackPacket = self.constructAckPacket(addr[1],recvBase)
                sock.sendto(ackPacket, (self.senderIp, addr[1]))
                ...
                continue
            else:
                print("data:", data)
                recvBuffer +=data
                recvBase +=1

                # 发送ack
                ackPacket = self.constructAckPacket(addr[1],recvBase) 
                sock.sendto(ackPacket, (self.senderIp, addr[1]))
    ```


## 4.结果展示

Go Back N:
```
1. run `python receiver.py`,
2. run `python testChannal.py`.
3. run `python sender.py`
```

接收方:
```
==========================================
recive seq: 7195
 
data: b'9 6A 8A 6A AA 6A 8A 6A 8A 6A 8A 6A 8A 72 6A 72 6A 72 6A 72 6A 72 '
 
Sended ack.
==========================================
recive seq: 7196
 
data: b'68 72 68 72 6A 72 6A 72 6A 72 8A 72 6A 72 6A 72 8A 72 8A 00 CC '
 
Sended ack.
==========================================
recive seq: 7197
 
data: b''
 
Sended ack.
==========================================
```
发送方：
```
ack:  7197
ack:  7198
Warning: buffer is empty.
tranfer finish!
```

比较文件差异：
```
diff testdata.txt recv_data.bin
```
无差异，成功。

