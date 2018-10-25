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
dropCount = 0
# Goes through events to gather bandwidths in list
for output in outputs:
    event = re.split('\s', output)
    # Checks that only "received" events are counted for bandwidth
    if event[EVENT] == 'd':
        dropCount += 1

print dropCount