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

"""Report timing data from a DAGMan run

Eg: ./timing.py header
"""

import argparse
from datetime import timedelta

# The arguments here are used to construct the list of data files

parser = argparse.ArgumentParser(__doc__)
parser.add_argument('header', help='the name of the output and/or job files')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args = parser.parse_args()

dag_log = f'{args.header}__dag.job.nodes.log'

time_list = []

total = count = 0

with open(dag_log, 'r') as f:
    for line in f:
        if 'Total Remote' in line:
            h, m, s = [int(s) for s in line.split(',')[0].split()[2].split(':')]
            total += 3600*h + 60*m + s
            count += 1

result = f'{dag_log}: total run time = {timedelta(seconds=total)}, ' \
         f'mean run time ({count} jobs) = {timedelta(seconds=int(total/count))}'

print(result)