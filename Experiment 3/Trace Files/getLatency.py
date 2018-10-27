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

# Distinguishes between flows. Now must be kept in list of throughputs per half-second interval
tcpLatency = []
cbrLatency = []

# Used for getting first iteration of events with the same "times"
# Dictionary maps whether the loop has went through first list or not to time
firstIteration = {}

i = 0
# The outputs only go up to 10 seconds
while (i < 10):
    firstIteration[i] = True
    i += 0.5
previousInterval = 0

def getTime(event, k, fromNode) :
    packetId = event[PKT_ID]
    receiveTime = float(event[TIME])
    sendTime = 0.0

    # Uses nested loop to get total time for all packets
    # This is necessary because multiple packets' sending and receiving times overlap with one another
    j = k
    while j > 0:
        pastEvent = re.split('\s', outputs[j])
        if pastEvent[PKT_ID] == packetId and pastEvent[EVENT] == '+' and pastEvent[FROM_NODE] == fromNode:
                sendTime = float(pastEvent[TIME])
                break
        j -= 1
    time = receiveTime - sendTime
    return time

i = 0
while i < len(outputs):
    eventCheck = re.split('\s', outputs[i])
    time = float(eventCheck[TIME])

    if float(eventCheck[TIME]) > 0.4 and 0 <= time % 0.5 < 0.001:
        index = time - time % 0.5
        if firstIteration[index] == True:
            tcpSumTime = 0.0
            tcpPacketCount = 0

            cbrSumTime = 0.0
            cbrPacketCount = 0

            # gets events from previous half-second interval to current
            k = previousInterval
            while k < i:
                event = re.split('\s', outputs[k])
                if event[EVENT] == 'r':
                    if event[FLOW_ID] == '1':
                        if event[TO_NODE] == '3':
                            tcpSumTime += getTime(event, k, '0')
                            tcpPacketCount += 1
                else:
                    if event[TO_NODE] == '5':
                        cbrSumTime += getTime(event, k, '4')
                        cbrPacketCount += 1
                k += 1
            # Each throughput put in a list, in Kbps
            # Check that time isn't zero so that it doesn't get the first seconds where only TCP runs
            if tcpPacketCount != 0:
                tcpLatency.append(tcpSumTime / tcpPacketCount * 2 * 1000)
            if cbrPacketCount != 0:
                cbrLatency.append(cbrSumTime / cbrPacketCount * 2 * 1000)
            previousInterval = i
            firstIteration[index] = False
    i += 1

# Round trip time, in milliseconds
# Displayed as TCP then CBR
for t in tcpLatency:
    print t
print "\n\n"
for t in cbrLatency:
    print t