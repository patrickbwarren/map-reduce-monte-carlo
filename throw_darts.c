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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "pcg64.h"
#include "throw_darts.h"

static pcg64_random_t rng;      /* PCG64 random number generator */
static uint64_t useed, ustream; /* The RNG seed and stream */

static int verbose = 0;

/* Stuff to do with radial distribution function */
/* The final bin records throws outside the target */

static int *gr = NULL; /* Integer array for bin counts */
static int nbins;      /* number of bins */
static double delg;    /* bin spacing in r */

/* Initialise with seed and sequence, and number of bins */

void initialise_target(int iseed, int istream, int inbins) {
  useed = (uint64_t)iseed;
  ustream = (uint64_t)istream;
  pcg64_srandom_r(&rng, useed, ustream);
  nbins = inbins; delg = 1.0 / nbins;
  if ((gr = (int *) malloc((1+nbins)*sizeof(int))) == NULL) {
    fprintf(stderr, "no space for gr at line %i in %s\n", __LINE__, __FILE__);
    exit(1);
  }
  reset();
}

/* Reset to zero counts */

void reset() {
  int i;
  for (i=0; i<(1+nbins); i++) gr[i] = 0;
}

/* Throw n darts at the target of unit radius and bin by distance from
   centre */

void throw(int n) {
  int i, ig;
  double x, y, r2;
  for (i=0; i<n; i++) {
    x = 2.0 * pcg64_random_d(&rng) - 1.0;
    y = 2.0 * pcg64_random_d(&rng) - 1.0;
    r2 = x*x + y*y;
    if (r2 < 1.0) ig = (int)(sqrt(r2)/delg);
    else ig = nbins;
    gr[ig]++;
  }
}

/* Return the current estimate for pi - the bin count are all inside
   the target of area pi, and gr[nbins] counts those outside. */

double pi_estimate() {
  int ig, ncount = 0;
  double area_square = 4.0;
  for (ig=0; ig<nbins; ig++) ncount += gr[ig];
  return area_square * (double)(ncount) / (double)(ncount + gr[nbins]);
}

/* Radial distribution function from centre of target */

void gr_write(char *filename, char *mode) {
  int ig, norm = 0;
  double r, g, area_shell, area_square = 4.0;
  FILE *fp;
  if ((fp = fopen(filename, mode)) == NULL) {
    printf("gr_write: %s could not be opened\n", filename); 
  } else {
    for (ig=0; ig<=nbins; ig++) norm += gr[ig];
    for (ig=0; ig<nbins; ig++) {
      r = delg * (ig+0.5);
      area_shell = M_PI*((ig+1)*(ig+1) - ig*ig)*delg*delg;
      g = (double)gr[ig] * area_square / ((double)norm * area_shell);
      fprintf(fp, "%g\tgr__%g\n", g, r);
    }
    fclose(fp);
  }
  if (verbose > 1) {
    printf("written data to %s, mode %s\n", filename, mode);
  }
}

void print_uint64(char *s, uint64_t v) {
  printf("uint64 %s = %#018" PRIx64 " = %" PRIu64 "ULL\n", s, v, v);
}

void report() {
  int ig, ncount = 0;
  for (ig=0; ig<nbins; ig++) ncount += gr[ig];
  print_uint64("seed", useed);
  print_uint64("stream", ustream);
  printf("nsuccess / nthrows = %i / %i\n", ncount, ncount + gr[nbins]);
}

void set_verbosity(int val) {
  verbose = val;
}

/* End of throw_darts.c */
