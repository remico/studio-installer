#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of "Ubuntu Studio Installer" project

#  Copyright (c) 2020, REMICO
#
#  The software is provided "as is", without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose and non-infringement. In no event shall the
#  authors or copyright holders be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.

"""INI-like config files handler"""

from pathlib import Path

from spawned import SpawnedSU, Spawned, create_py_script

from .configfilebase import ConfigFileBase
from .. import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['IniConfig']


_tp = util.tagged_printer('[IniConfig]')

_re_script = create_py_script(r"""
import fileinput
import re, sys

_a = sys.argv
filepath = _a[1]
re_pattern = _a[2]
replacement = _a[3]

with fileinput.FileInput(filepath, inplace=True) as f:
    for line in f:
        print(re.sub(re_pattern, replacement, line), end='')
""")


class IniConfig(ConfigFileBase):
    def replace(self, re_old: str, str_new: str):
        if not Path(self.abs_filepath).exists():
            _tp(f"File '{self.abs_filepath}' doesn't exist. No replacement done.")
            return

        cmd = f"python3 {_re_script} {self.filepath} {re_old} {str_new}"
        self._execute(cmd)
