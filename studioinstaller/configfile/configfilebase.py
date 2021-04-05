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

"""Base file for config files handlers"""

from abc import abstractmethod, ABC

from spawned import SpawnedSU, Spawned

from .. import util

__all__ = ['ConfigFileBase']


class ConfigFileBase(ABC):
    def __init__(self, filepath, chroot_context=None):
        self.chroot_cntx = chroot_context
        self.filepath = filepath
        self.abs_filepath = '/'.join([chroot_context.root, filepath]) if chroot_context else filepath

    def __iter__(self):
        return self.content.__iter__()

    def _execute(self, cmd: str, edit=True):
        """Execute a shell command ``cmd`` in a chroot jail or in current file system"""
        if self.chroot_cntx:
            owner = util.system.owner_uid(self.stat)
            self.chroot_cntx.do(cmd, user=owner)
        else:
            condition = util.system.is_editable(self.stat) if edit else util.system.is_readable(self.stat)
            S_ = Spawned if condition else SpawnedSU
            S_.do_script(cmd, timeout=Spawned.TIMEOUT_DEFAULT, bg=False)

    @abstractmethod
    def replace(self, re_old: str, str_new: str):
        pass

    def append(self, str_new: str):
        cmd = f'printf "\n{str_new}\n" >> {self.filepath}'
        self._execute(cmd)

    @property
    def stat(self):
        self._st = None
        if not self._st:
            self._st = util.system.os_stat(self.abs_filepath)
        return self._st

    @property
    def content(self):
        lines = Spawned(f"cat {self.abs_filepath}", sudo=not util.system.is_readable(self.stat)).datalines
        return [line_stripped for line in lines if (line_stripped := line.strip())]
