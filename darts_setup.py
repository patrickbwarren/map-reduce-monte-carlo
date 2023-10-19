#!/usr/bin/env python3

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

"""setup.py file for Map/Reduce Monte-Carlo darts example"""

from setuptools import setup, Extension

ThrowDarts_module = Extension('_ThrowDarts', sources=['ThrowDarts_wrap.c', 'throw_darts.c'])

setup(name='ThrowDarts',
      version='1.0',
      author="Patrick B Warren",
      description="""Map/Reduce Monte-Carlo example""",
      ext_modules=[ThrowDarts_module],
      py_modules=["ThrowDarts"])
