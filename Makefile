# This file is part of MRMC - a demonstrator for Map/Reduce
# Monte-Carlo methods.

# MRMC is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MRMC is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>.

# You should have received a copy of the GNU General Public License
# along with MRMC.  If not, see <http://www.gnu.org/licenses/>.

default_target : MRMC

MRMC_wrap.c : MRMC.i mrmc.h
	swig -python MRMC.i

MRMC : setup.py MRMC.i MRMC_wrap.c mrmc.c mrmc.h
	python setup.py build_ext --inplace

test-pcg64 : pcg64.h test-pcg64.c
	gcc -Wall -O3 -o $@ $@.c

clean :
	rm -f MRMC.py MRMC_wrap.c _MRMC*.so
	rm -rf build
	rm -f test-pcg64

pristine : clean
	rm -f *~
