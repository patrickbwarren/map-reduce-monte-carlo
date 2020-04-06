/*
This file is part of a demonstrator for Map/Reduce Monte-Carlo
methods.

This is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your
option) any later version.

This is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>.

You should have received a copy of the GNU General Public License
along with this file.  If not, see <http://www.gnu.org/licenses/>.
*/

/* Test PCG64 independent random number streams */

/* The options in here are -s sets the seed, -n sets the number of
random doubles, and -m sets the number of streams. */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include "pcg64.h"

static struct option long_options[] = {
  {"seed",    required_argument, 0, 's'},
  {"nrandom",  required_argument, 0, 'n'},
  {"mstreams",  required_argument, 0, 'm'},
  {0, 0, 0, 0}
};

int main(int argc, char** argv) {
  int i, k, c;
  int mstreams = 2;
  int nrandom = 1000;
  int option_index = 0;
  uint64_t seed = 12345ULL;
  pcg64_random_t *rng; /* for an array of these things */
  while (1) {
    c = getopt_long(argc, argv, "s:n:m:", long_options, &option_index);
    if (c == -1) break;
    switch (c) {
    case 's': seed = (uint64_t)atoi(optarg); break;
    case 'n': nrandom = atoi(optarg); break;
    case 'm': mstreams = atoi(optarg); break;
    }
  }
  rng = (pcg64_random_t *)malloc(mstreams*sizeof(pcg64_random_t));
  for (i=0; i<mstreams; i++) {
    pcg64_srandom_r(&rng[i], seed, (uint64_t)i); /* fixed seed, seq advances */
  }
  for (k=0; k<nrandom; k++) {
    for (i=0; i<mstreams; i++) {
      printf("%0.17g%c", pcg64_random_d(&rng[i]), (i<mstreams-1)?'\t':'\n');
    }
  }
  return 0;
}
