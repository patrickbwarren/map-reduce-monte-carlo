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
wrap any kind of Monte-Carlo code, with some straightforward
requirements on the output format.

### Wrapper scripts

`wrapper.py`


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
distributed on [0, 1) is 1/12).  For 10<sup>5</sup> the residuals
should be down around 10<sup>&minus;4</sup> to 10<sup>&minus;5</sup>.

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

