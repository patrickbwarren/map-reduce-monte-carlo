/**
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
**/

#ifndef THROW_DARTS_H
#define THROW_DARTS_H

void initialise_target(int, int, int);
void reset();
void throw(int);
double pi_estimate();
void gr_write(char *, char *);
void report();
void set_verbosity(int);

#endif /* THROW_DARTS_H */
