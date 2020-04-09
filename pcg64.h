/*
 * PCG64 Random Number Generation for C.
 *
 * Copyright 2014 Melissa O'Neill <oneill@pcg-random.org>
 * Copyright 2015 Robert Kern <robert.kern@gmail.com>
 *
 * Modification copyright 2020 Patrick B Warren <patrickbwarren@gmail.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * For additional information about the PCG random number generation scheme,
 * including its license and other licensing options, visit
 *
 *     http://www.pcg-random.org
 */

#ifndef PCG64_H_INCLUDED
#define PCG64_H_INCLUDED

#include <inttypes.h>

typedef __uint128_t pcg128_t;

#define PCG_128BIT_CONSTANT(high, low) (((pcg128_t)(high) << 64) + low)

typedef struct {
  pcg128_t state;
  pcg128_t inc;
} pcg64_random_t;

#define PCG_DEFAULT_MULTIPLIER_128 PCG_128BIT_CONSTANT(2549297995355413924ULL, \
						       4865540595714422341ULL)

#define PCG64_INITIALIZER						\
  { PCG_128BIT_CONSTANT(0x979c9a98d8462005ULL, 0x7d3e9cb6cfe0549bULL),	\
      PCG_128BIT_CONSTANT(0x0000000000000001ULL, 0xda3e39cb94b95bdbULL) }

static inline uint64_t pcg_rotr_64(uint64_t value, unsigned int rot) {
  return (value >> rot) | (value << ((- rot) & 63));
}

static inline void pcg_setseq_128_step_r(pcg64_random_t* rng) {
  rng->state = rng->state * PCG_DEFAULT_MULTIPLIER_128 + rng->inc;
}

static inline uint64_t pcg_output_xsl_rr_128_64(pcg128_t state) {
  return pcg_rotr_64(((uint64_t)(state >> 64u)) ^
		     (uint64_t)state, state >> 122u);
}

static inline void pcg64_srandom_r(pcg64_random_t* rng, uint64_t seed,
				   uint64_t stream) {
  rng->state = 0U;
  rng->inc = ((__uint128_t)stream << 1u) | 1u;
  pcg_setseq_128_step_r(rng);
  rng->state += (__uint128_t)seed;
  pcg_setseq_128_step_r(rng);
}

static inline uint64_t pcg64_random_r(pcg64_random_t* rng) {
  pcg_setseq_128_step_r(rng);
  return pcg_output_xsl_rr_128_64(rng->state);
}

static inline uint64_t pcg64_boundedrand_r(pcg64_random_t* rng,
					   uint64_t bound) {
  uint64_t threshold = -bound % bound;
  for (;;) {
    uint64_t r = pcg64_random_r(rng);
    if (r >= threshold)
      return r % bound;
  }
}

static inline double pcg64_random_d(pcg64_random_t* rng) {
  uint64_t x = pcg64_random_r(rng);
  return (x >> 11) * (1.0 / 9007199254740992.0);
}

#endif /* PCG64_H_INCLUDED */
