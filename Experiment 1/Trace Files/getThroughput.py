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
packetSizeSum = 0
timeSum = 0.0

i = 0
while i < len(outputs):
    event = re.split('\s', outputs[i])
    if (event[EVENT] == 'r' and event[FLOW_ID] == '1'):
        # Gets sum of packet size for throughput calculation later
        packetSize = float(event[PKT_SIZE])
        packetSizeSum += packetSize

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
        timeSum += time
    i += 1


# Calculated in Kbps
throughput = packetSizeSum/timeSum*8/1000
print throughput