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
f1DropCount = 0
f2DropCount = 0
f3DropCount = 0

# Goes through outputs
for output in outputs:
    event = re.split('\s', output)

    # Collects dropped packet count
    if event[EVENT] == 'd':
        if event[FLOW_ID] == '1':
            f1DropCount += 1
        elif event[FLOW_ID] == '2':
            f2DropCount += 1
        elif event[FLOW_ID] == '3':
            f3DropCount += 1
        else:
            print "There are more than the allowed number of flows for experiment 2."
            exit()

print f1DropCount, f2DropCount, f3DropCount