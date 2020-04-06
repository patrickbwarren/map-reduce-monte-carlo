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

# Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>
# apart from where otherise stated.

# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

"""Wrapper to map jobs onto a condor cluster

Eg: ./mapper.py throw_darts.py --header=mytest --seed=12345 --ntrial=10
 --nthrow=10^6  --njobs=8 --module=ThrowDarts
"""

import os
import sys
import argparse
import subprocess

# keep this to include in the job description

command_line = ' '.join(sys.argv)

# The following code snippet comes from
# https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse

def add_bool_arg(parser, name, default=False, help=None):
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true',
                       help=help + (' (default)' if default else ''))
    group.add_argument('--no-' + name, dest=name, action='store_false',
                       help="don't " +help + (' (default)' if not default else ''))
    parser.set_defaults(**{name:default})
    
parser = argparse.ArgumentParser(__doc__)
parser.add_argument("script", help="script to be run")
parser.add_argument('--module', default=None, help='supporting module(s), default None')
parser.add_argument('--exts', default="['.so', '.py']", help='file extensions for modules')
parser.add_argument('--header', required=True, help='the name of the output and/or job files')
parser.add_argument('--njobs', required=True, type=int, help='the number of condor jobs')
parser.add_argument('--fast', action='store_true', help='if set, run with Mips > min mips')
parser.add_argument('--min-mips', type=int, default=20000, help='min mips for fast option')
add_bool_arg(parser, 'reduce', default=True, help='use DAGMan to reduce the output')
add_bool_arg(parser, 'clean', default=True, help='clean up intermediate output files')
add_bool_arg(parser, 'launch', help='launch the condor DAGMan master job')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args, rest = parser.parse_known_args()

# Extract a list of modules from the argument

if args.module:
    try:
        modules = eval(args.module)
    except NameError:
        modules = [args.module]
else:
    modules = []

# Find the files to transfer associated with these modules.  After
# this transfer_files will be a list of files in the current directory
# which have an extension in args.file_ext and where the file name
# matches any of the modules in args.modules.

extensions = eval(args.exts)

file_list = [f.name for f in os.scandir() if f.is_file()] # names of all files in current directory

if modules:
    transfer_files = list(filter(lambda f: any(f.endswith(e) for e in extensions)
                               and any(m in f for m in modules), file_list))
else:
    transfer_files = []

transfer_files.append(args.script)

# Create the condor job file

condor_job = args.header + '__condor.job'

# Add a requirements line if requested and extra options if
# required (newlines are required to insert as lines)

extra = ''

if args.fast:
    extra += 'requirements = Mips > %i' % args.min_mips + '\n'

# Reconstruct the verbose option and stick on the end of the unmatched arguments

if args.verbose:
    rest.append('-' + 'v' * args.verbose)
    
opts = ' '.join(rest) # now contains all the unmatched arguments

# The actual job description using an f-string

job = f"""# {command_line}
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
notification = never
universe = vanilla
opts = {opts}
{extra}transfer_input_files = {','.join(transfer_files)}
executable = /usr/bin/python
arguments = {args.script} --header={args.header} $(opts) --process=$(Process)
output = {args.header}__$(Process).out
error = {args.header}__$(Process).err
queue {args.njobs}"""

with open(condor_job, 'w') as f:
    f.write(job + '\n')

if args.verbose:
    print('Created:', condor_job)

if not args.reduce: # we just need to run the condor job

    launch_command = 'condor_submit ' + condor_job

else: # otherwise create a DAGMan master job

    dag_job = args.header + '__dag.job'

    opt_clean = '--clean' if args.clean else '--no-clean'

    dag = f"JOB A {condor_job}\n" \
          f"SCRIPT POST A {sys.executable} reducer.py --header={args.header} --njobs={args.njobs} {opt_clean}"

    with open(dag_job, 'w') as f:
        f.write(dag + '\n')

    if args.verbose:
        print('Created:', dag_job)

    launch_command = 'condor_submit_dag -notification Never ' + dag_job

# We launch if required, otherwise print out the launch command for the user

if args.launch: 
    subprocess.call(launch_command, shell=True)
else:
    print(launch_command)

# Write out some information if required
