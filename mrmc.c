/**
This file is part of MRMC - a demonstrator for Map/Reduce Monte-Carlo
methods.

MRMC is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your
option) any later version.

MRMC is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>.

You should have received a copy of the GNU General Public License
along with MRMC.  If not, see <http://www.gnu.org/licenses/>.
**/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "pcg64.h"
#include "mrmc.h"

static pcg64_random_t rng;   /* PCG64 random number generator */
static uint64_t seed, seq;   /* The RNG seed and sequence */
static int nsuccess, ntrial; /* Number of successes, trials */

static int verbose = 0;

/* Stuff to do with radial distribution function */

static int *gr = NULL; /* Integer array for bin counts */
static int nbins;      /* number of bins */
static double delg;    /* bin spacing in r */

/* Initialise with seed and sequence, and number of bins */

void initialise_target(int iseed, int iseq, int nbinss) {
  seed = (uint64_t)iseed;
  seq = (uint64_t)iseq;
  pcg64_srandom_r(&rng, seed, seq);
  nbins = nbinss; delg = 1.0 / nbins;
  if ((gr = (int *) malloc((1+nbins)*sizeof(int))) == NULL) {
    fprintf(stderr, "no space for gr at line %i in %s\n", __LINE__, __FILE__);
    exit(1);
  }
  reset();
}

/* Reset to zero counts */

void reset() {
  int i;
  nsuccess = ntrial = 0;
  for (i=0; i<(1+nbins); i++) gr[i] = 0;
}

/* Throw ntrial darts at the target and record the cumulative number
   of successes and bin the distance from corner by r^2*/

void throw(int n) {
  int i, ig, c = 0;
  double x, y, r2;
  for (i=0; i<n; i++) {
    x = pcg64_random_d(&rng);
    y = pcg64_random_d(&rng);
    r2 = x*x + y*y;
    if (r2 < 1.0) {
      ig = (int)(sqrt(r2)/delg); c++;
    } else {
      ig = nbins;
    }
    gr[ig]++;
  }
  nsuccess += c; ntrial += n;
}

/* Return the current estimate for pi */

double pi_estimate() {
  return 4.0 * (double)nsuccess / (double)ntrial;
}

/* Radial distribution function from centre of target */

void gr_write(char *filename, char *mode) {
  int ig, norm;
  double r, area_shell, g;
  FILE *fp;
  if ((fp = fopen(filename, mode)) == NULL) {
    printf("gr_write: %s could not be opened\n", filename); 
  } else {
    norm = 0; for (ig=0; ig<=nbins; ig++) norm += gr[ig];
    for (ig=0; ig<nbins; ig++) {
      r = delg * (ig+0.5);
      area_shell = 0.25 * M_PI*((ig+1)*(ig+1) - ig*ig)*delg*delg;
      g = (double)gr[ig] / ((double)norm * area_shell);
      fprintf(fp, "gr__%g\t%g\n", r, g);
    }
    fclose(fp);
  }
  if (verbose > 1) {
    printf("written data to %s, mode %s\n", filename, mode);
  }
}

void report() {
  printf("uint64 seed = %#018" PRIx64 " = %" PRIu64 "ULL\n", seed, seed);
  printf("uint64 seq  = %#018" PRIx64 " = %" PRIu64 "ULL\n", seq, seq);
  printf("nsuccess / ntrial = %i / %i\n", nsuccess, ntrial);
}

void set_verbosity(int val) {
  verbose = val;
}

/* End of mrmc.c */
