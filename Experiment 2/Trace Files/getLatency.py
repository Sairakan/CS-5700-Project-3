import os
import sys
import re
import argparse

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

# Latency must now be separated by flow
f1SumTime = 0.0
f2SumTime = 0.0
f3SumTime = 0.0
f1DroppedPackets = 0
f2DroppedPackets = 0
f3DroppedPackets = 0

# To get number of packets, separated by flow
f1PacketCount = 0
f2PacketCount = 0
f3PacketCount = 0

def getTime(event) :
    packetId = event[PKT_ID]
    receiveTime = float(event[TIME])
    sendTime = 0.0

    # Uses nested loop to get total time for all packets
    # This is necessary because multiple packets' sending and receiving times overlap with one another
    j = i
    while j > 0:
        pastEvent = re.split('\s', outputs[j])
        if pastEvent[PKT_ID] == packetId and pastEvent[EVENT] == '+':
                sendTime = float(pastEvent[TIME])
                break
        j -= 1
    time = receiveTime - sendTime
    return time

i = 0
while i < len(outputs):
    event = re.split('\s', outputs[i])

    if (event[FLOW_ID] == '1'):
        # Don't count dropped packets to account for round trip time
        if (event[EVENT] == 'd'):
            f1DroppedPackets += 1
        elif (event[EVENT] == 'r'):
            f1SumTime += getTime(event)
            f1PacketCount += 1
    elif (event[FLOW_ID] == '2'):
        if (event[EVENT] == 'd'):
            f2DroppedPackets += 1
        elif (event[EVENT] == 'r'):
            f2SumTime += getTime(event)
            f2PacketCount += 1
    elif (event[FLOW_ID] == '3'):
        if (event[EVENT] == 'd'):
            f3DroppedPackets += 1
        elif (event[EVENT] == 'r'):
            f3SumTime += getTime(event)
            f3PacketCount += 1
    else:
        print "There are more than the allowed number of flows for experiment 2."
        exit()
    i += 1

# Round trip time, in milliseconds
# Displayed as flow 1, flow 2, then flow 3
f1Latency = f1SumTime / f1PacketCount * 2 * 1000
f2Latency = f2SumTime / f2PacketCount * 2 * 1000
f3Latency = f3SumTime / f3PacketCount * 2 * 1000
print f1Latency, f2Latency, f3Latency