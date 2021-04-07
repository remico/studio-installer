#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of "Linux Studio Installer" project
#
#  Author: Roman Gladyshev <remicollab@gmail.com>
#  License: MIT License
#
#  SPDX-License-Identifier: MIT
#  License text is available in the LICENSE file and online:
#  http://www.opensource.org/licenses/MIT
#
#  Copyright (c) 2020 remico

"""/etc/fstab handler"""

from copy import copy
from functools import singledispatchmethod
from pathlib import Path

from spawned import Spawned

from .configfilebase import ConfigFileBase
from .. import util

__all__ = ['FstabConfig', 'FstabItem']


_tlog = util.tagged_logger('[FstabConfig]')


class FstabItem:
    def __init__(self, volume, mountpoint, fs, opts, dump=0, pass_=2):
        self.volume = volume
        self.mountpoint = mountpoint
        self.fs = fs
        self.opts = opts
        self.dump = dump
        self.pass_ = pass_

        self.origin = copy(self)

    def __repr__(self):
        return f"FstabItem({self.volume}, {self.mountpoint}, {self.fs}, [{self.opts}], {self.dump}, {self.pass_})"

    def __str__(self):
        return f"{self.volume}  {self.mountpoint}  {self.fs}  {self.opts}  {self.dump}  {self.pass_}"

    @staticmethod
    def build(fstab_line: str):
        return FstabItem(*fstab_line.split())

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


class FstabConfig(ConfigFileBase):
    def __init__(self, chroot_context=None):
        super().__init__('/etc/fstab', chroot_context)

    def __iter__(self):
        return self.items.__iter__()

    def replace(self, old: FstabItem, new: FstabItem):
        if not Path(self.abs_filepath).exists():
            _tlog(f"File '{self.abs_filepath}' doesn't exist. No replacement done.")
            return

        re_old = r'[\s\t]+'.join(str(old).split())
        cmd = util.cmd_edit_inplace(self.filepath, re_old, str(new))
        self._execute(cmd)

    def save(self, item: FstabItem):
        if item.origin:
            self.replace(item.origin, item)

    def contains(self, partition):
        lvm_lv_vid = f"/dev/mapper/{partition.lvm_vg.replace('-', '--')}-{partition.lvm_lv}"
        return bool(Spawned.do(f"egrep '{partition.url}|{partition.uuid}|{lvm_lv_vid}' {self.abs_filepath}"))

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
