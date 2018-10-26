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

def getPacketSizeAndTime (event, k):
    # Gets sum of packet size for throughput calculation later
    packetSize = float(event[PKT_SIZE])

    packetId = event[PKT_ID]
    receiveTime = float(event[TIME])
    sendTime = 0.0

    # Uses nested loop to get total time for all packets
    # This is necessary because multiple packets' sending and receiving times overlap with one another
    j = k
    while j > 0:
        pastEvent = re.split('\s', outputs[j])
        if pastEvent[PKT_ID] == packetId and pastEvent[EVENT] == '+':
                sendTime = float(pastEvent[TIME])
                break
        j -= 1
    time = receiveTime - sendTime
    return packetSize, time

# Distinguishes between flows. Now must be kept in list of throughputs per half-second interval
tcpThroughput = []
cbrThroughput = []

# Used for getting first iteration of events with the same "times"
# Dictionary maps whether the loop has went through first list or not to time
firstIteration = {}

i = 0
# The outputs only go up to 10 seconds
while (i < 10):
    firstIteration[i] = True
    i += 0.5
previousInterval = 0
print firstIteration
i = 0
while i < len(outputs):
    eventCheck = re.split('\s', outputs[i])

    time = float(eventCheck[TIME])

    # loops through to find half-second points of outputs
    # the modulus check interval is necessary in case there's no exact 0.5 second interval
    if float(eventCheck[TIME]) > 0.4 and 0 <= time % 0.5 < 0.001:
        index = time - time % 0.5
        if firstIteration[index] == True:
            tcpIntervalSumPacketSize = 0
            tcpIntervalSumTime = 0
            cbrIntervalSumPacketSize = 0
            cbrIntervalSumTime = 0
            # gets events from previous half-second interval to current
            k = previousInterval
            while k < i:
                event = re.split('\s', outputs[k])
                if event[EVENT] == 'r':
                    if (event[FLOW_ID] == '1'):
                        packetSizeAndTime = getPacketSizeAndTime(event,k)
                        tcpIntervalSumPacketSize += packetSizeAndTime[0]
                        tcpIntervalSumTime += packetSizeAndTime[1]
                    else:
                        packetSizeAndTime = getPacketSizeAndTime(event,k)
                        cbrIntervalSumPacketSize += packetSizeAndTime[0]
                        cbrIntervalSumTime += packetSizeAndTime[1]
                k +=1
            # Each throughput in a list, in Kbps
            if tcpIntervalSumTime != 0:
                tcpThroughput.append((float(eventCheck[TIME]), tcpIntervalSumPacketSize/tcpIntervalSumTime*8/1000))

            # Check that time isn't zero so that it doesn't get the first seconds where only TCP runs
            if cbrIntervalSumTime != 0:
                cbrThroughput.append((float(eventCheck[TIME]), cbrIntervalSumPacketSize/cbrIntervalSumTime*8/1000))

            previousInterval = i
            firstIteration[index] = False
    i += 1

# Printed in order of flow. TCP then CBR
print tcpThroughput
print cbrThroughput