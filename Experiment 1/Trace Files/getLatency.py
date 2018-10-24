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

# Gets the last output because time is measured as "time elapsed"
event = re.split('\s', outputs[-1])
time = float(event[TIME])
# packet ID is autoincremented in the trace file from zero, making the number of packets the ID + 1
numPackets = int(event[PKT_ID]) + 1

# Round trip time, in milliseconds
latency = time / numPackets * 2 * 1000
print latency