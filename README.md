# BackTCP-Protocal
A connection-less reliable transmission protocal implemented in python

# Aim 
The aim is to implement backTCP protocal. 
Sender: read file to sender buffer, then encapsule the segmentation with backTCP header, then send the package to receiver
Receiver: send ACK to sender

# 本质问题
1. 接收方应该干什么？ 接收包，然后检查序列号，发送ack number给sender。接受方发送的报文只需要包含header！然后header里面序列号为0，只用acknumber是重要的。
sender每发送一次包就要等待一次receiver发送的ack包。如果等待时间超过timer时间，就重传 （Figure 3.33）
2. 

# To do list
step1. 实现本地127.0.0.1端口的sender和receiver（此时不会丢包），打印header检查（使用unittest？）
step2，在助教的信道上测试

