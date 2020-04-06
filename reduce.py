#!/usr/bin/env python

import argparse
import numpy as np

# The arguments here are used to construct the list of data files

parser = argparse.ArgumentParser()
parser.add_argument('--header', required=True, help='set the name of the output and/or job files')
parser.add_argument('--njobs', required=True, type=int, help='the number of condor jobs')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args = parser.parse_args()

with open(args.header + '.log', 'r') as f:
    for line in f:
        if 'data collected for' in line:
            data_types = line.split(':')[1].split()


for data_type in data_types:
    data = {}
    for i in range(args.njobs):
        data_file = f'{args.header}_{data_type}__{i}.dat'
        with open(data_file, 'r') as f:
            for line in f:
                code, val = line.split('\t')
                if code in data:
                    data[code].append(val)
                else:
                    data[code] = [val]
    data_file = f'{args.header}_{data_type}.dat'
    with open(data_file, 'w') as f:
        for code in data:
            arr = np.array([float(v) for v in data[code]])
            mean = np.mean(arr)
            var = np.var(arr, ddof=1)
            n = np.size(arr)
            f.write('%s\t%g\t%g\t%d\n' % (code, mean, np.sqrt(var/n), n))
    print(data_type + ' > ' + data_file)

# we need to clean up by removing the .err and .out and data files
# so we need an argment for clean logs and clean data
# and suggest an argument for the log file extensions ['.out', '.err']
    
# end of script
