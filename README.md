## Map/Reduce Monte-Carlo framework

Provides a framework for high-throughput parallelisation of
Monte-Carlo codes in a distributed computing environment, using the
[HTCondor](https://research.cs.wisc.edu/htcondor/) ('condor')
scheduling system.

### Outline

> In Hartree's opinion [ca 1951] all the calculations that would ever
   be needed [in the UK] could be done on three digital computers.
   &mdash; *B. V. Bowden*

A typical Monte-Carlo simulation consists of generating samples at
random, for which some property or properties are measured.  For
example, for liquid states one might measure thermodynamic properties
like energy and pressure, and structural properties like pair
distribution functions and structure factors.  It is important to
ensure that different samples are uncorrelated, otherwise a false
estimate of the accuracy is generated.

If we have to generate *N*
samples, one way to do this is to do *n* independent runs, each
generating *N* / *n* samples, and to combine the output.  This
approach is ideally suited for task farming, or high-throughput
parallelisation in a distributed computing environment.  Because of
the resemblence to
[MapReduce](https://en.wikipedia.org/wiki/MapReduce) in computing, I
term this Map/Reduce Monte-Carlo.

This repository contains python scripts `mapper.py` and `reducer.py`,
and an example code that illustrates the approach.  The scripts can
launch pretty much any kind of scripted Monte-Carlo code across a
condor cluster, with some straightforward requirements on the output
format.

The example provided is a 'toy model' Monte-Carlo simulation of
throwing darts at a target.
 
### Quick summary

Make sure [HTCondor](https://research.cs.wisc.edu/htcondor/) is
installed and running on the target system.

To build and run the dart-throwing example do `make`, followed by
```console
./mapper.py throw_darts.py --header=mytest --seed=12345 --ntrial=10 \
--nthrow=10^6 --njobs=8 --module=ThrowDarts --run
```
This should result in a DAGMan job being launched, which after it
completes leaves a number of `mytest__*` job files, plus
`mytest_pi.dat` which contains an estimate of &pi; computed from the
number of darts which fall within a unit disc centred on the origin,
`mytest_gr.dat` which contains the radial distribution data for the
dart positions, and `mytest.log` contains some log information.

### Scripts

The main script for launching jobs across a condor cluster is `mapper.py`:
```console
usage: Map jobs onto a condor cluster

       [-h] --header HEADER --njobs NJOBS [--fast] [--run]
       [--min-mips MIN_MIPS] [--modules MODULES] [--extensions EXTENSIONS]
       [--transfers TRANSFERS] [--reduce | --no-reduce] [--clean | --no-clean]
       [--prepend | --no-prepend] [-v]
       script

positional arguments:
  script           script to be run

optional arguments:
  -h, --help               show this help message and exit
  --header HEADER          set the name of the output and/or job files
  --njobs NJOBS            the number of condor jobs
  --fast                   run with Mips > min_mips
  --run                    run the condor or DAGMan job
  --min-mips MIN_MIPS      min_mips for fast option, default 20000
  --modules MODULES        supporting module(s), default None
  --extensions EXTENSIONS  file extensions for module(s), default .so,.py
  --transfers TRANSFERS    additional files to transfer, default None
  --(no-)reduce            use DAGMan to reduce the output (default yes)
  --(no-)clean             clean up intermediate files (default yes)
  --(no-)prepend           prepend mapper call to log file (default yes)
  -v, --verbose            increasing verbosity
```
After the jobs have completed, if `--reduce` is set (the default) the
DAGMan job calls `reducer.py`:
```console
usage: Reduce outputs from jobs run on a condor cluster

       [-h] --header HEADER [--njobs NJOBS] [--extensions EXTENSIONS]
       [--clean | --no-clean] [--prepend | --no-prepend] [-v]

optional arguments:
  -h, --help               show this help message and exit
  --header HEADER          set the name of the output and/or job files
  --njobs NJOBS            the number of condor jobs
  --extensions EXTENSIONS  file extensions for cleaning, default out,err
  --(no-)clean             clean up intermediate files (default no)
  --(no-)prepend           prepend mapper call to log file (default yes)
  -v, --verbose            increasing verbosity
```
Note that by default `mapper.py` invokes `reducer.py` with the `--clean` option.

Finally, timing information can be extracted with a helper script `timing.py`:
```console
./timing.py --help
usage: Report timing data from a DAGMan run

       [-h] [-v] header

positional arguments:
  header         the name of the output and/or job files

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increasing verbosity
```

### Requirements

In order to work, the above scripts make some assumptions about the
behaviour of the script driving the Monte-Carlo code, which is
presumed either to be pure python (or perl), or a python script which
wraps an underlying library, or with some modifications a python
script that itself runs a separate stand-alone binary package.

The script `mapper.py` launches `--njobs` condor jobs which run the
designated script, *passing on any unused options*.  Thus any options
required by the script should be included in the command line as
indicated in the example below.  In addition, the script to be run
should accept the following options:

`--header=<header>` : a string to specify the names of output files;  
`--process=<proc_id>` : an integer to label data files;  
`-v`, `--verbose` : should be allowed even if they don't do anything.

Usually one would also include a `--seed` option which is passed onto
each instance of the script unchanged.  Thus the script should
generate random numbers using a combination of `--seed` and
`--process`.  How this might be done is detailed below.

For output, the script should generate data files with names
```
<header>_<data_type>__<proc_id>.dat
```
where the `<data_type>` is a string which can be used to discriminate
between different types of data.  Each entry (line) in a data file should be
of the form
```
<tag>\t<measurement>
```
where `<tag>` is used to label the measurement, and `<measurement>` is
the actual numerical value, and the two are separated by a tab (`\t`).

Using tags it is possible to combine different data types in the same
file.  One use-case exemplified by the radial distribution function is
to incorporate a numerical value into the tag, for example `gr__<r>`
with `<r>` being the bin radial distance mid-point.  The double
underscore can be removed afterwards for downstream analysis and
plotting purposes.

In addition to the data files, the script should generate a log file
of the form `<header>.log`, to contain a line in the form
```
data collected for: <list_of_data_types>
```
The comma-separated list of data types here tells `reducer.py` which
`<data_type>` output files should be reduced.

### Outputs

The effect of running `mapper.py` on a script which meets the above
rules, and assuming `--reduce` is set (the default), is to generate
output data files of the form
```
<header>_<data_type>.dat
```
These contain reduced data in the form
```
<tag>\t<mean_measurement>\t<std_error>\t<ncount>
```
reporting the mean and standard error in the measured values computed
from the raw data from the intermediate output files (`reducer.py`
uses NumPy to do this calculation).  If `--clean` is set (the default
in `mapper.py`) then the intermediate files are deleted.

In addition a number of job and log files of the form `<header>__*`
are left; these can also be safely deleted if not required.  A timing
summary can be extracted from `<header>__dag.job.nodes.log` by running
`timing.py <header>`.

Finally, the actual `mapper.py` command line is prepended to the log
file, unless `--no-prepend` is indicated.  This means that the job can
be re-run if necessary.

### Example: throwing darts 

As an example of a Monte-Carlo problem, consider throwing darts at
random in a 2-dimensional square domain with &minus;1 &le; *x* < 1 and
&minus;1 &le; *y* < 1.  The distance *r* from the centre is measured,
where *r*<sup>2</sup> = *x*<sup>2</sup> + *y*<sup>2</sup>.  The value
of &pi; can be estimated by counting the number of points with *r*
&le; 1 since the number of such points &approx; &pi;&rho; where &rho;
= *N* / *A* is the density of points, given that *N* is the total
number of dart throws and *A* = 4 is the area of the square domain.
The radial distribution of dart distances from the centre should of
course be flat, and can be computed by binning in *r* and taking into
account the annulus areas of the bins.  This calculation is directly
analogous to computing a radial distribution function in a liquid.

This Monte-Carlo problem is implemented in C in `throw_darts.h`
and `throw_darts.c`, with `pcg64.h` for random number generation (see
below).  These codes provide function calls which are wrapped 
with [SWIG](http://www.swig.org/), using
[distutils](https://docs.python.org/3/library/distutils.html) to
process `darts_setup.py` to obtain a python module `ThrowDarts.py` and
a supporting shared object (`.so`) library.  This build is the default
target in the `Makefile`.

A run is controlled by the python driver script `throw_darts.py`:
```console
./throw_darts.py --help
usage: Throw darts at a target to estimate pi, and measure radial distribution

       throw_darts.py [-h] --header HEADER [--seed SEED] [--process PROCESS]
                      [--ntrial NTRIAL] [--nthrow NTHROW] [--nbins NBINS] [-v]

optional arguments:
  -h, --help         show this help message and exit
  --header HEADER    set the name of the output files
  --seed SEED        the RNG seed, default 12345
  --process PROCESS  process number, default None
  --ntrial NTRIAL    number of trials, default 10
  --nthrow NTHROW    number of throws per trial, default 1000
  --nbins NBINS      number of bins in rdf, default 20
  -v, --verbose      increasing verbosity
```
This driver script produces a `<header>.log` file which contains a line
describing the output data files (in this case `<header>_pi__*.dat`
containing the estimates of &pi; and `<header>_gr__*.dat` containing
the radial distribution).  Each separate trial generates its own
estimates, and the results are appended to the data files (one can
reduce these by hand using `reducer.py` and omitting the `--njobs` option).
The `--process` option for `throw_darts.py` tags the output data file
names appropriately.  

The above code and driver script thus meet the requirements of
`mapper.py`, and for example a batch run of 8 jobs can be launched
with the command
```console
./mapper.py throw_darts.py --header=mytest --seed=12345 --ntrial=10 \
 --nthrow=10^6 --njobs=8 --module=ThrowDarts --run
 ```
This will result in the files `mytest_pi.dat` and `mytest_gr.dat`
being generated, containing the combined reduced data.  A plot of the
radial distribution function can be obtained by replacing double
underscores by tabs in the data file, as
```console
sed -i.bak s/__/\\t/ mytest_gr.dat 
```
(this keeps a backup in `mytest_gr.dat.bak`).  The resulting data set
can be visualised by plotting columns 2, 3, and 4 of `mytest_gr.dat`
as respectively *r*, *g*(*r*), and &Delta;*g*(*r*) where *g*(*r*) is the
radial distribution function estimate (mean) and &Delta;*g*(*r*) is the
associated standard error.  If you do this, notice that the standard
error decreases as *r* increases.  The reason is that there are more
data points in the bins further away from the origin, since the area
of the bin annulus increases with *r*.

### Random number generation

> Random numbers should not be generated with a method chosen at
   random. &mdash; *Donald E. Knuth*

> Anyone who attempts to generate random numbers by deterministic
  means is, of course, living in a state of sin. &mdash; *John von Neumann*

In order to work within the Map/Reduce Monte-Carlo paradigm, it is
essential that each separate run should have access
to an *independent* (and thread-safe if necessary) stream of high
quality random numbers.  Equally, it is important for regression
testing to be able to seed these random number streams in a repeatable
way.  Fortunately there are modern solutions to this problem, for
instance the [permutation congruential generator (PCG)
family](https://www.pcg-random.org/) of random number generators
(RNGs) can efficiently supply independent streams from a single seed.

In this repository the PCG64 variant is encoded as static inline
functions in a C header file `pcg64.h`. The code is based on
https://github.com/rkern/pcg64 and on the PCG64 implementation in
[NumPy](https://github.com/numpy/numpy/tree/master/numpy/random).

For the purposes of the above demonstration, one only needs the following
interface:
```c
#include "pcg64.h"

pcg64_random_t rng; // Create an instance of the RNG

uint64_t seed, seq; // seed the RNG
pcg64_srandom_r(&rng, seed, seq);

double x; // get a random double
x = pcg64_random_d(&rng);
```
(for additional functions providing random integers see `pcg64.h`)

In the above `seed` is an unsigned long integer (`uint64_t`) which is
the RNG seed, and `seq` is another unsigned long integer which selects
which stream is generated.  Thus to generate *n* independent streams
from a common seed, one should set `seed` equal to the given value,
and `seq` equal to 0 to *n* &minus; 1.

The code `test-pcg64.c` demonstrates this (`make test-pcg64` is a
target in the `Makefile`).  Running this for example with
```console
./test-pcg64 -s 12345 -n 100000 -m 5 > out.txt
```
captures the output in `out.txt` (`-s` sets the seed, `-n` sets the
number of random doubles, and `-m` sets the number of streams).
One can then check for correlations between the streams using
```python
import numpy as np
arr = np.loadtxt('out.txt')
cov = np.cov(arr.transpose())
with np.printoptions(precision=3, suppress=True):
    print(cov)
with np.printoptions(precision=3):
    print(cov-np.eye(*np.shape(cov))/12.0)
```
This prints out first the covariance matrix (in this case 5 &times;
5), and then the residuals (the variance of a random number uniformly
distributed on [0, 1) is 1/12).  For 10<sup>5</sup> random numbers as
above the residuals should be down around 10<sup>&minus;4</sup> to
10<sup>&minus;5</sup>.

> Spengler: Don't cross [correlate] the streams.  
  Venkman: Why ?  
  Spengler: It would be bad.  
  Venkman: I'm fuzzy on the whole good / bad thing. What do you mean
  "bad" ?  
  Spengler: Try to imagine all life as you know it stopping
  instantaneously and every molecule in your body exploding at the
  speed of light.  
  Stantz: Total protonic reversal.  
  Venkman: That's bad. Okay. All right. Important
  safety tip.  Thanks, Egon.  
  &mdash; *Ghostbusters*

In the dart throwing example, `--seed` is used to set the RNG seed
and `--process` is used to set the sequence.  The conversion to the
required `uint64_t` types is done in the C code.

### Copying

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see
<http://www.gnu.org/licenses/>.

The file `pcg64.h` is licensed under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>.

### Copyright

Copyright &copy; 2020 Patrick B Warren <patrickbwarren@gmail.com>.

The [PCG64 RNG](https://www.pcg-random.org/) is based on 
<https://github.com/rkern/pcg64> and on
[NumPy](https://github.com/numpy/numpy/tree/master/numpy/random)  

Copyright &copy; 2014 Melissa O'Neill <oneill@pcg-random.org>.  
Copyright &copy; 2015 Robert Kern <robert.kern@gmail.com>.

### Contact

Email: <patrickbwarren@gmail.com>

