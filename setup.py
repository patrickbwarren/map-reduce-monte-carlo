#!/usr/bin/env python

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

"""
setup.py file for Map/Reduce Monte-Carlo example
"""

from distutils.core import setup, Extension

MRMC_module = Extension('_MRMC', sources=['MRMC_wrap.c', 'mrmc.c'])

setup(name='MRMC',
      version='1.0',
      author="Patrick B Warren",
      description="""Map/Reduce Monte-Carlo example""",
      ext_modules=[MRMC_module],
      py_modules=["MRMC"])
