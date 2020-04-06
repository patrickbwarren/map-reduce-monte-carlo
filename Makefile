# This file is part of a demonstrator for Map/Reduce Monte-Carlo
# methods.

# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# Copyright (c) 2020 Patrick B Warren <patrickbwarren@gmail.com>.

# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

default_target : ThrowDarts

ThrowDarts_wrap.c : ThrowDarts.i throw_darts.h
	swig -python ThrowDarts.i

ThrowDarts : darts_setup.py ThrowDarts.i ThrowDarts_wrap.c throw_darts.c throw_darts.h
	python darts_setup.py build_ext --inplace

test-pcg64 : pcg64.h test-pcg64.c
	gcc -Wall -O2 -o $@ $@.c

clean :
	rm -f ThrowDarts.py ThrowDarts_wrap.c _ThrowDarts*.so
	rm -rf build
	rm -f test-pcg64

pristine : clean
	rm -f *~
