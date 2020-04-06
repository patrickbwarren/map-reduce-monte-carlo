#!/usr/bin/env python

# This file is part of a demonstrator for Map/Reduce Monte-Carlo
# methods.

# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>.

# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

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
