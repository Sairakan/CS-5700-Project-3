import os
import sys
import re
import argparse

argp = argparse.ArgumentParser(
    description='ns2pp - ns-2 Python Parser.\n\n' +
                '- For each flow-node pair, a .DAT file will be generated.\n' +
                '- A gnuplot script will be generated ready to plot those .DAT ' +
                  'files.',
    epilog='ns2pp Copyright (C) 2015 Ricardo Oliveira {rgoliveira@inf.ufrgs.br}\n' +
           'This program comes with ABSOLUTELY NO WARRANTY.\n' +
           'This is free software, and you are welcome to redistribute it\n' +
           'under certain conditions.\n' +
           'See <http://www.gnu.org/licenses/> for more information.\n',
    usage="%(prog)s <tracefile> [options]",
    formatter_class=argparse.RawDescriptionHelpFormatter)
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

# Has to be stored in tuple of (packetId, latency) to keep track of and remove dropped packets
latencies = []

# Goes through events
for line in outputs:
    event = re.split('\s', line)

    if event[EVENT] == 'd':
        for latency in latencies:
            if latency[0] == event[PKT_ID]:
                latencies.remove(latency)
    else:
        time = float(event[TIME])
        latencies.append((event[PKT_ID], time))

latencySum = sum(latency[1] for latency in latencies)

avgLatency = latencySum / len(latencies)
print avgLatency