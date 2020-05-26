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

"""Partitions hierarchy"""

from .partitionbase import Partition
from ...spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['FS']


class FS(Partition):
    def format(self):
        if "efi" in self.mountpoint:
            cmd = "mkfs.vfat -F32 %s"
        elif self.mountpoint == "/boot":
            cmd = "mkfs.ext2 %s"
        elif self.mountpoint == "swap":
            cmd = "mkswap %s"
        elif self.fs:
            cmd = f"mkfs.{self.fs} %s"
        else:
            cmd = "mkfs.ext4 %s"
        SpawnedSU.do(cmd % self.url)

    def mount(self, chroot=None):
        mountpoint = chroot or self.mountpoint
        if mountpoint and not self.isswap:
            SpawnedSU.do(f"mount {self.url} {mountpoint}")
        elif self.isswap:
            SpawnedSU.do(f"swapon {self.url}")

    def umount(self):
        if not self.isswap:
            SpawnedSU.do(f"umount {self.url}")
        else:
            SpawnedSU.do(f"swapoff {self.url}")
