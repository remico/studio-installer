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

"""Make file system"""

from .actionbase import ActionBase
from ..spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Format']


class Format(ActionBase):
    def __next__(self):
        return super().__next__()

    def iterator(self, scheme):
        # filter only partitions to be formatted
        self.nodes.extend([pt for pt in scheme if pt.do_format or pt.isswap])
        return self

    @staticmethod
    def _format(partition):
        if "efi" in partition.mountpoint:
            cmd = "mkfs.vfat -F32 %s"
        elif partition.mountpoint == "/boot":
            cmd = "mkfs.ext2 %s"
        elif partition.mountpoint == "swap":
            cmd = "mkswap %s"
        elif partition.fs:
            cmd = f"mkfs.{partition.fs} %s"
        else:
            cmd = "mkfs.ext4 %s"
        SpawnedSU.do(cmd % partition.url)

    def serve_standard_pv(self, pt):
        self._format(pt)

    def serve_luks_pv(self, pt):
        pass

    def serve_lvm_on_luks_vg(self, pt):
        pass

    def serve_lvm_lv(self, pt):
        self._format(pt)
