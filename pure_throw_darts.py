#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

"""Throw darts at a target to estimate pi, and measure radial distribution (pure python version)

Eg: ./throw_darts.py --header=mytest --seed=12345 --ntrial=100 --nthrow=10^6 -v
"""

import argparse
import numpy as np

# Parse the argument list

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--header', required=True, help='set the name of the output files')
parser.add_argument('--seed', default=12345, type=int, help='the RNG seed, default 12345')
parser.add_argument('--process', default=0, type=int, help='process number, default 0')
parser.add_argument('--njobs', default=1, type=int, help='the number of condor jobs, deault 1')
parser.add_argument('--ntrials', default=10, type=int, help='number of trials, default 10')
parser.add_argument('--nthrows', default='1000', help='number of throws per trial, default 1000')
parser.add_argument('--nbins', default='20', type=int, help='number of bins in rdf, default 20')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args = parser.parse_args()

ntrials, nbins = args.ntrials, args.nbins
nthrows = eval(args.nthrows.replace('^', '**')) # catch 10^6 etc

pid, njobs = args.process, args.njobs
local_rng = np.random.default_rng(seed=args.seed).spawn(njobs)[pid] # select a local RNG stream

gr_bins = np.zeros(1+nbins, dtype=int)

pi_estimate = np.zeros(ntrials)

pi_file = '%s__%d_pi.dat' % (args.header, pid)
gr_file = '%s__%d_gr.dat' % (args.header, pid)
log_file = '%s.log' % args.header

for trial in range(ntrials):
    gr_bins[:] = 0
    for throw in range(nthrows):
        x, y = local_rng.uniform(-1.0, 1.0, 2)
        ig = min(nbins, int(np.sqrt(x**2+y**2)*nbins))
        gr_bins[ig] = gr_bins[ig] + 1
    pi_estimate[trial] = 4.0 * np.sum(gr_bins[:-1]) / nthrows
    mode = 'w' if trial == 0 else 'a'
    with open(gr_file, mode) as f:
        for ig in range(nbins):
            r = (ig + 0.5) / nbins
            area_annulus = np.pi * ((ig+1)**2 - ig**2) / nbins**2
            g = 4.0 * gr_bins[ig] / (nthrows * area_annulus)
            f.write('%g\tgr__%g\n' % (g, r))

with open(pi_file, 'w') as f:
    for x in pi_estimate:
        f.write('%g\tpi\n' % x)

run_opts = [f'--header={args.header}', f'--seed={args.seed}',
            f'--ntrials={ntrials}', f'--nthrows={nthrows}',
            f'--nbins={nbins}']

if args.process == 0:
    with open(log_file, 'w') as f:
        f.write(f'# {__file__}\n')
        f.write('# opts: ' + ' '.join(run_opts) + '\n')
        f.write('# data collected for: pi, gr\n')
