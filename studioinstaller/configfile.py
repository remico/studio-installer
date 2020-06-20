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

"""Edit config files content"""

import os
import stat
from pathlib import Path

from spawned import SpawnedSU, Spawned, create_py_script

from . import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['ConfigFile']


_tp = util.tagged_printer('[ConfigFile]')

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


class ConfigFile:
    def __init__(self, filepath, chroot_context=None):
        self.chroot_cntx = chroot_context
        self.filepath = filepath
        self.abs_filepath = '/'.join([chroot_context.root, filepath]) if chroot_context else filepath

    def apply(self, re_pattern, replacement):
        if not Path(self.abs_filepath).exists():
            _tp(f"File '{self.abs_filepath}' doesn't exist. No replacement done.")
            return

        cmd = f"python3 {_re_script} {self.filepath} {re_pattern} {replacement}"

        if self.chroot_cntx:
            self.chroot_cntx.do(cmd, user=self.owner)
        else:
            S = Spawned if self.iseditable else SpawnedSU
            S.do_script(cmd, timeout=Spawned.TO_DEFAULT, bg=False)

    @property
    def stat(self):
        self._st = None
        if not self._st:
            self._st = os.stat(self.abs_filepath)
        return self._st

    @property
    def iseditable(self):
        return bool(self.stat.st_mode & (stat.S_IWUSR | stat.S_IWGRP))

    @property
    def owner(self):
        return self.stat.st_uid
