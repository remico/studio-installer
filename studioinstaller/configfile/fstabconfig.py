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
from pathlib import Path

from spawned import create_py_script

from .configfilebase import ConfigFileBase
from .. import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['FstabConfig', 'FstabItem']


_tp = util.tagged_printer('[FstabConfig]')


class FstabItem:
    def __init__(self, volume, mountpoint, fs, opts, dump=0, pass_=2):
        self.volume = volume
        self.mountpoint = mountpoint
        self.fs = fs
        self.opts = opts
        self.dump = dump
        self.pass_ = pass_

        self.origin = None  # original line from /etc/fstab

    def __repr__(self):
        return f"FstabItem({self.volume}, {self.mountpoint}, {self.fs}, [{self.opts}], {self.dump}, {self.pass_})"

    def __str__(self):
        return f"{self.volume}  {self.mountpoint}  {self.fs}  {self.opts}  {self.dump}  {self.pass_}"

    @staticmethod
    def build(fstab_line: str):
        item = FstabItem(*fstab_line.split())
        item.origin = fstab_line
        return item

    @property
    def options(self):
        return self.opts.split(',')

    def add_option(self, option: str):
        self.opts += f",{option}"

    def delete_option(self, option: str):
        try:
            options = self.opts.split(',')
            options.remove(option)
            self.opts = ','.join(options)
        except ValueError as e:
            print(f"WARNING: {__class__.__name__}.delete_option('{option}'): {e}")


_re_script = create_py_script(r"""
import fileinput
import re, sys

_a = sys.argv
filepath = _a[1]
old_str = _a[2]
new_str = _a[3]

with fileinput.FileInput(filepath, inplace=True) as f:
    for line in f:
        print(line.replace(old_str, new_str), end='')
""")


class FstabConfig(ConfigFileBase):
    def __init__(self, chroot_context=None):
        super().__init__('/etc/fstab', chroot_context)

    def __iter__(self):
        return self.items.__iter__()

    def replace(self, old: str, new: str):
        if not Path(self.abs_filepath).exists():
            _tp(f"File '{self.abs_filepath}' doesn't exist. No replacement done.")
            return

        cmd = f'python3 "{_re_script}" "{self.filepath}" "{old}" "{new}"'
        print(cmd)
        self._execute(cmd)

    def save(self, item: FstabItem):
        if item.origin:
            self.replace(item.origin, str(item))

    @singledispatchmethod
    def append(self, item: FstabItem):
        super().append(str(item))

    @append.register(str)
    def _(self, volume, mountpoint, fs, opts, dump=0, pass_=2):
        self.append(FstabItem(volume, mountpoint, fs, opts, dump, pass_))

    @property
    def items(self):
        active_lines = [line for line in super().__iter__() if not line.startswith('#')]
        return [FstabItem.build(line) for line in active_lines]
