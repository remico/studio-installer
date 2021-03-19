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

"""Make file system"""

from spawned import SpawnedSU
from .actionbase import ActionBase

__all__ = ['Format']


def _options(partition):
        opts = []
        if partition.fs == "btrfs":
            opts.append('-f')
        return ' '.join(opts)


class Format(ActionBase):
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
            cmd = f"mkfs.{partition.fs} {_options(partition)} %s"
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

    def serve_encrypted_vv(self, pt):
        self._format(pt)
