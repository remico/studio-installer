#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .partitionbase import Partition
from ...spawned import SpawnedSU

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
