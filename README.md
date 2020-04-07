## Map/Reduce Monte-Carlo framework

Provides a framework for high-throughput parallelisation of
Monte-Carlo codes in a distributed computing environment, using the
HTCondor scheduling system.

### Outline

> In Hartree's opinion [ca 1951] all the calculations that would ever
   be needed [in the UK] could be done on three digital computers.
   &mdash; *B. V. Bowden*

A typical Monte-Carlo simulation consists of generating samples at
random, for which some property or properties are measured.  For
example for liquid states, measuring thermodynamic properties like energy
and pressure, and structural properties like pair distribution
functions and structure factors.  It is important to ensure that
different samples are uncorrelated, otherwise a false perception of
the accuracy is generated.  If we have to generate *N* samples, one
way to do this is to do *n* indepdent runs, each generating *N* / *n*
samples, and to combine the output.  This approach is ideally suited
for task farming, or high-throughput parallelisation in a distributed
computing environment.  Because of the resemblence to
[MapReduce](https://en.wikipedia.org/wiki/MapReduce) in computing, I
term this Map/Reduce Monte-Carlo.

This repository contains python scripts `mapper.py` and `reducer.py`
and an example code that illustrates the approach.  The scripts can
launch pretty much any kind of Monte-Carlo code across a
[HTCondor](https://research.cs.wisc.edu/htcondor/) cluster, with some
straightforward requirements on the output format.

### Scripts

This is the main script for launching jobs across a condor cluster.
```console
./mapper.py --help
usage: Map jobs onto a condor cluster

Eg: ./mapper.py throw_darts.py --header=mytest --seed=12345 --ntrial=10 \
 --nthrow=10^6 --njobs=8 --module=ThrowDarts

       [-h] [--module MODULE] [--exts EXTS] --header HEADER --njobs NJOBS
       [--fast] [--min-mips MIN_MIPS] [--reduce | --no-reduce]
       [--clean | --no-clean] [--launch | --no-launch] [-v]
       script

positional arguments:
  script               script to be run
  
optional arguments:
  -h, --help           show this help message and exit
  --module MODULE      supporting module(s), default None
  --exts EXTS          file extensions for modules
  --header HEADER      set the name of the output and intermediate files
  --njobs NJOBS        the number of condor jobs
  --fast               if set, run with Mips > min mips
  --min-mips MIN_MIPS  min mips for fast option
  --reduce             use DAGMan to reduce the output (default)
  --no-reduce          don't use DAGMan to reduce the output
  --clean              clean up intermediate files (default)
  --no-clean           don't clean up intermediate files
  --launch             launch the condor or DAGMan job
  --no-launch          don't launch the condor or DAGMan job (default)
  -v, --verbose        increasing verbosity
```
The above automatically calls `reducer.py` if `--reduce` is set.
```console
./reducer.py --help
usage: Reduce outputs from jobs run on a condor cluster

Eg: ./reducer.py --header=mytest --njobs=8

       [-h] --header HEADER [--njobs NJOBS] [--exts EXTS]
       [--clean | --no-clean] [-v]

optional arguments:
  -h, --help       show this help message and exit
  --header HEADER  set the name of the output and/or job files
  --njobs NJOBS    the number of condor jobs
  --exts EXTS      file extensions for cleaning
  --clean          clean up intermediate files
  --no-clean       don't clean up intermediate files (default)
  -v, --verbose    increasing verbosity
```
Note that by default `mapper.py` invokes `reducer.py` with the `--clean` option.

Timing information on the run can be extracted with the helper script
```console
./timing.py --help
usage: Report timing data from a DAGMan run

Eg: ./timing.py header

       [-h] [-v] header

positional arguments:
  header         the name of the output and/or job files

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increasing verbosity
```

### Requirements

### Example: throwing darts 

As an example of a Monte-Carlo problem, I consider throwing darts
(*x*, *y*) at random in a 2-dimensional square domain with &minus;1
&le; *x* < 1 and &minus;1 &le; *y* < 1.  The distance *r* from the
centre is measured, where *r*<sup>2</sup> = *x*<sup>2</sup> +
*y*<sup>2</sup>.  The value of &pi; can be estimated by counting the
number of points with *r* &le; 1 since the number of such points
&approx; &pi;&rho; where &rho; = *N* / *A* the density of points, *N*
is the total number of dart throws, and *A* = 4 is the area of the
square domain.  The radial distribution of dart distances from the
centre should of course be flat, and can be computed by binning *r*
and taking into account the target annulus areas of the bins.  This
part is taken directly from analogous code to compute the radial
distribution function in a liquid.

This Monte-Carlo problem is implemented in the C codes `throw_darts.h`
and `throw_darts.c`, with `pcg64.h` for random number generation (see
below).  These codes provide function calls which are accessed by
wrapping with [SWIG](http://www.swig.org/) and using
[distutils](https://docs.python.org/3/library/distutils.html) to
process `darts_setup.py` to obtain a python module `ThrowDarts.py` and
a supporting shared object (`.so`) library.

The python driver script `throw_darts.py` controls a run
```console
./throw_darts.py --help
usage: throw_darts.py [-h] --header HEADER [--seed SEED] [--process PROCESS]
                      [--ntrial NTRIAL] [--nthrow NTHROW] [--nbins NBINS] [-v]

Throw darts at a target to estimate pi, and measure radial distribution Eg:
./throw_darts.py --header=mytest --seed=12345 --ntrial=100 --nthrow=10^6 -v

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
This script produces a `<header>.log` file which contains a line
describing the output data files, and in this case `<header>_pi.dat`
to contain the estimates of &pi; and `<header>_gr.dat` containing
the radial distribution.  Each trial generates its own
estimates, and the results are appended to the data files (one can
reduce these by hand by using `reducer.py` omitting the `--njobs` option).
The `--process` option for `throw_darts.py` tags the data file names
so that they can be processed appropriately after using `mapper.py` to
launch a batch of jobs.

The above code and driver script is designed to meet the requirements
of `mapper.py` and thus for example a batch run of 8 jobs can be
launched with the command
```console
./mapper.py throw_darts.py --header=mytest --seed=12345 --ntrial=10 \
 --nthrow=10^6 --njobs=8 --module=ThrowDarts --launch
 ```
This will result in the files `mytest_pi.dat` and `mytest_gr.dat`
being generated, containing the combined reduced data.  A plot of the
radial distribution function can be obtained by replacing double
underscore by tab in the file, with
```console
sed -i.bak s/__/\\t/ mytest_gr.dat 
```

(this keeps a backup in `mytest_gr.dat.bak`).  The resulting
`mytest_gr.dat` can be visualised by plotting columns 2, 3, and 4 as
respectively *r*, *y*, and &delta;*y* where *y* is the radial
distribution function estimate (mean) and &delta;*y* is the associated
standard error.  If you do this, note that the standard error
decreases as *r* increases.  The reason is that there are more data
points in the bins further away from the origin, since the area of
the bin annulus increases with *r*.

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

For the purposes of the demonstration, one only needs the following
interface:
```c
#include "pcg64.h"

pcg64_random_t rng; // Create an instance of the RNG

uint64_t seed, seq; // seed the RNG
pcg64_srandom_r(&rng, seed, seq);

double x; // get a random double
x = pcg64_random_d(&rng);
```
(for functions providing random integers see `pcg64.h`)

In the above `seed` is an unsigned long integer (`uint64_t`) which is
the RNG seed, and `seq` is another unsigned long integer which selects
which stream is generated.  Thus to generate *n* independent streams
from a common seed, one should set `seed` equal to the given value,
and `seq` equal to 0 to *n* &minus; 1.  The code `test-pcg64.c`
demonstrates this: `make test-pcg64` s a target in the Makefile.  If
the output is captured in `out.txt`, for example (`-s` sets the seed,
`-n` sets the number of random doubles, and `-m` sets the number of
streams):
```bash
./test-pcg64 -s 12345 -n 100000 -m 5 > out.txt
```
then one can check for correlations between the streams using
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

