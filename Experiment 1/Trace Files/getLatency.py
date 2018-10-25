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

i = 0

sumTime = 0.0
droppedPackets = 0

while i < len(outputs):
    event = re.split('\s', outputs[i])

    # Don't count dropped packets to account for round trip time
    if (event[EVENT] == 'd'):
        droppedPackets += 1

    if (event[EVENT] == 'r'):
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
        sumTime += time
    i += 1

numPackets = int(re.split('\s', outputs[-1])[PKT_ID]) + 1 - droppedPackets
# Round trip time, in milliseconds
latency = sumTime / numPackets * 2 * 1000
print latency