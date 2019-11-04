
# to be continued

1. 实现Sender的流水线发送
    同时实现 Go-back-N 与 选择重传 ``mode = "Go-Back-N" or "Select" ``
2. 实现Receiver类:

    a. 接受包并检查seqNum ``recvOnePack()`` 

    b. 发送ack包,ack包的payload为空 ``sendAck()``

    c. 对接收到的包进行整理(选择重传情况下) ``sortRecvPack()``
    
    d. Go-back-N情况下，把之前的包都丢掉。
3. 本地测试，打印过程。
