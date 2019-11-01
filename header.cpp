#include<stdlib.h>

typedef struct backTcpHeader{
    u_int16_t srcPort;
    u_int16_t recvPort;
    u_int8_t seqNum;
    u_int8_t ackNum;
    u_int8_t offset;
    u_int8_t winSize;
    u_int8_t reFlag;
}backTcpHeader

int constructHeader(){
    
}