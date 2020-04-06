#!/usr/bin/env python

import os
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("script", help="script to be run")
parser.add_argument('--module', default=None, help='the supporting module(s)')
parser.add_argument('--extensions', default="['.so', '.py']", help='set file extensions for modules')
parser.add_argument('--header', required=True, help='set the name of the output and/or job files')
parser.add_argument('--njobs', required=True, type=int, help='the number of condor jobs')
parser.add_argument('--fast', action='store_true', help='if set, run with Mips > min mips')
parser.add_argument('--min-mips', type=int, default=20000, help='min mips for fast option')
parser.add_argument('--launch', action='store_true', help='if set, launch the condor DAGMan master job')
parser.add_argument('--no-clean', action='store_true', help='if set, leave in place the individual condor job outputs')
parser.add_argument('-v', '--verbose', action='count', default=0, help='increasing verbosity')
args, rest = parser.parse_known_args()

# Extract a list of modules from the argument

try:
    modules = eval(args.module)
except NameError:
    modules = [args.module]

# Find the files to transfer associated with these modules.  After
# this module_files will be a list (actually an iterable) of files in
# the current directory which have an extension in args.extensions and
# where the file name matches any of the modules in args.modules.

extensions = eval(args.extensions)
file_list = [f.name for f in os.scandir() if f.is_file()] # names of all files in current directory
module_files = filter(lambda f: any(f.endswith(e) for e in extensions) and any(m in f for m in modules), file_list)

dag_job = args.header + '__dag.job'
condor_job = args.header + '__condor.job'

# Create a requirements line if requested and extra options if
# required (newlines are required to insert as lines)

extra = ''

if args.fast:
    extra += 'requirements = Mips > %i' % args.min_mips + '\n'

# reconstruct the verbose option and stick on the end of the unmatched arguments
    
if args.verbose:
    rest.append('-' + 'v' * args.verbose)
    
opts = ' '.join(rest) # now contains all the unmatched arguments

# The condor job description using an f-string

job = f"""should_transfer_files = YES
when_to_transfer_output = ON_EXIT
notification = never
universe = vanilla
opts = {opts}
{extra}transfer_input_files = {','.join(module_files)},{args.script}
executable = /usr/bin/python
arguments = {args.script} --header={args.header} $(opts) --process=$(Process)
output = {args.header}__$(Process).out
error = {args.header}__$(Process).err
queue {args.njobs}"""

with open(condor_job, 'w') as f:
    f.write(job + '\n')

# The DAGMan master job using an f-string

dag = f"""JOB A {condor_job}
SCRIPT POST A python gather.py""" # more in here ...

with open(dag_job, 'w') as f:
    f.write(dag + '\n')

# This is the command that will launch the DAGMan master job

dag_launch = 'condor_submit_dag -notification Never ' + dag_job

# We launch the job, if required, otherwise print out the command for the user

if args.launch: 
    subprocess.call(dag_launch, shell=True)
else:
    print(dag_launch)

# Write out some information if required

if args.verbose:
    print('Created', ', '.join([dag_job, condor_job]))
