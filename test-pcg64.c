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

/* Test PCG64 independent random number streams by emitting 100,000
   pairs of random doubles */

#include <stdio.h>
#include "pcg64.h"

int main(int argc, char** argv) {
  int i, n = 100000;
  pcg64_random_t rng1, rng2;
  pcg64_srandom_r(&rng1, 12345ULL, 0ULL);
  pcg64_srandom_r(&rng2, 12345ULL, 1ULL);
  for (i=0; i<n; i++) {
    printf("%0.17g\t", pcg64_random_d(&rng1));
    printf("%0.17g\n", pcg64_random_d(&rng2));
  }
  return 0;
}
