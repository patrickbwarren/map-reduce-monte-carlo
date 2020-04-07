#!/usr/bin/env python3

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

"""Throw darts at a target to estimate pi, and measure radial distribution

Eg: ./throw_darts.py --header=mytest --seed=12345 --ntrial=100 --nthrow=10^6 -v
"""

import argparse
import ThrowDarts as darts

# Parse the argument list

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--header', action='store', required=True, help='set the name of the output files')
parser.add_argument('--seed', action='store', default=12345, type=int, help='the RNG seed, default 12345')
parser.add_argument('--process', action='store', default=None, type=int, help='process number, default None')
parser.add_argument('--ntrial', action='store', default=10, type=int, help='number of trials, default 10')
parser.add_argument('--nthrow', action='store', default='1000', help='number of throws per trial, default 1000')
parser.add_argument('--nbins', action='store', default='20', type=int, help='number of bins in rdf, default 20')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args = parser.parse_args()

nthrow = eval(args.nthrow.replace('^', '**')) # catch 10^6 etc

darts.set_verbosity(args.verbose)

files = {} # dictionary that will contain file names by data type

sub = '' if args.process is None else '__%d' % args.process

for data_type in ['pi', 'gr']:
    files[data_type] = '_'.join([args.header, data_type]) + sub + '.dat'
    
darts.initialise_target(args.seed, 0 if args.process is None else args.process, args.nbins)

# Run a number of simulations.

vals = [0] * args.ntrial # initialise array to save pi estimates

for k in range(0, args.ntrial):
    darts.reset()
    darts.throw(nthrow)
    vals[k] = darts.pi_estimate()
    darts.gr_write(files['gr'], 'a' if k else 'w') 
    if args.verbose > 1:
        darts.report()

# Save the pi estimate results to the 'pi' file

with open(files['pi'], 'w') as f:
    for x in vals:
        f.write('pi\t' + str(x) + '\n')

# Summarise the run to a log file using f-strings and a line 'data collected'

run_time = f'./{__file__} --header={args.header} --seed={args.seed}' \
           f' --ntrial={args.ntrial} --nthrow={args.nthrow} --nbins={args.nbins}'

if not args.process: # true if args.process is None or 0
    with open(args.header + '.log', 'w') as f:
        f.write('# ' + run_time + '\n')
        f.write('data collected for: ' + ' '.join(files.keys()) + '\n')

if args.verbose:
    print('Full command: ' + run_time)
    print('To reduce the data use: '+ f'python reducer.py --header={args.header}')
    print('Generated: ' + args.header + '.log, ' + ', '.join(files.values()))

# End of script
