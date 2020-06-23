#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of "Ubuntu Studio Installer" project
#
#  Copyright (c) 2020, REMICO
#
#  The software is provided "as is", without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose and non-infringement. In no event shall the
#  authors or copyright holders be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.

"""/etc/fstab handler"""

from functools import singledispatchmethod

from .configfilebase import ConfigFileBase
from .. import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['FstabConfig', 'FstabLine']


_tp = util.tagged_printer('[FstabConfig]')


class FstabLine:
    def __init__(self, volume, mountpoint, fs, opts, dump=0, pass_=2):
        self._line = f"{volume}  {mountpoint}  {fs}  {opts}  {dump}  {pass_}"

    def __repr__(self):
        return self._line


class FstabConfig(ConfigFileBase):
    def replace(self, re_old: str, str_new: str):
        _tp("INFO: replace() is not implemented for FstabConfig")

    @singledispatchmethod
    def append(self, str_new: FstabLine):
        super().append(str(str_new))

    @append.register(str)
    def _(self, volume, mountpoint, fs, opts, dump=0, pass_=2):
        self.append(FstabLine(volume, mountpoint, fs, opts, dump, pass_))
