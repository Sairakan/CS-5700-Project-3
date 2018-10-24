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
bandwidths = []

# Goes through events to gather bandwidths in array
for line in outputs:
    event = re.split('\s', line)
    
    # Checks that only "received" events are counted for bandwidth
    if event[EVENT] == 'r':
        packetSize = float(event[PKT_SIZE]) * 8.0
        time = float(event[TIME])

        # bandwidth is in bps
        bandwidth = packetSize/time
        bandwidths.append(bandwidth)

avgBandwidth = sum(bandwidths)/len(bandwidths)
print avgBandwidth