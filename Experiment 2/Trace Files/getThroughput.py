import os, sys, re, argparse, itertools

argp = argparse.ArgumentParser()
argp.add_argument('tracefile',
        type=argparse.FileType('r'),
        help="Ns2 trace file to be parsed")

args = argp.parse_args()

# Statics for looking through tracefile outputs
EVENT       = 0
TIME        = 1
FROM_NODE   = 2
TO_NODE     = 3
PKT_TYPE    = 4
PKT_SIZE    = 5
FLAGS       = 6
FLOW_ID     = 7
SRC_ADDR    = 8
DST_ADDR    = 9
SEQ_NUM     = 10
PKT_ID      = 11

outputs = [output for output in args.tracefile.read().splitlines()]

def getPacketSizeAndTime (event, fromNode):
    # Gets sum of packet size for throughput calculation later
    packetSize = float(event[PKT_SIZE])

    packetId = event[PKT_ID]
    receiveTime = float(event[TIME])
    sendTime = 0.0

    # Uses nested loop to get total time for all packets
    # This is necessary because multiple packets' sending and receiving times overlap with one another
    j = i
    while j > 0:
        pastEvent = re.split('\s', outputs[j])
        if pastEvent[PKT_ID] == packetId and pastEvent[EVENT] == '+' and pastEvent[FROM_NODE] == fromNode:
                sendTime = float(pastEvent[TIME])
                break
        j -= 1
    time = receiveTime - sendTime
    return packetSize, time

# Distinguishes between flows
f1PacketSizeSum = 0
f1TimeSum = 0.0
f2PacketSizeSum = 0
f2TimeSum = 0.0
f3PacketSizeSum = 0
f3TimeSum = 0.0

i = 0
while i < len(outputs):
    event = re.split('\s', outputs[i])
    if (event[EVENT] == 'r'):
        if (event[FLOW_ID] == '1' and event[TO_NODE] == '3'):
            packetSizeAndTime = getPacketSizeAndTime(event, '0')
            f1PacketSizeSum += packetSizeAndTime[0]
            f1TimeSum += packetSizeAndTime[1]
        elif (event[FLOW_ID] == '2' and event[TO_NODE] == '5'):
            packetSizeAndTime = getPacketSizeAndTime(event, '4')
            f2PacketSizeSum += packetSizeAndTime[0]
            f2TimeSum += packetSizeAndTime[1]
        elif (event[FLOW_ID] == '3' and event[TO_NODE] == '2'):
            packetSizeAndTime = getPacketSizeAndTime(event, '1')
            f3PacketSizeSum += packetSizeAndTime[0]
            f3TimeSum += packetSizeAndTime[1]
    i += 1


# Calculated in Kbps and displays flow 1, flow 2, then flow 3's throughputs
f1Throughput = f1PacketSizeSum/f1TimeSum*8/1000
f2Throughput = f2PacketSizeSum/f2TimeSum*8/1000
f3Throughput = f3PacketSizeSum/f3TimeSum*8/1000
print f1Throughput,'\t',f2Throughput,'\t',f3Throughput