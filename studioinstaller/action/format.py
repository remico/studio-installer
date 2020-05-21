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
from ..partition.base import VType

__all__ = ['Format']


def _options(partition):
        opts = []

        if partition.mountpoint == "swap":
            if partition.label:
                opts.append(f"-L {partition.label}")

        elif "efi" in partition.mountpoint:
            opts.append("-F32")

            if partition.label:
                opts.append(f"-n {partition.label}")

        elif partition.fs == "btrfs":
            opts.append('-f')

            if partition.label:
                opts.append(f"-L {partition.label}")

        elif "ext" in partition.fs:
            if partition.label:
                opts.append(f"-L {partition.label}")

        return ' '.join(opts)


class Format(ActionBase):
    def iterator(self, scheme):
        # filter only partitions to be formatted
        self.nodes.extend([pt for pt in scheme if pt.do_format or pt.isswap])
        return self

    @staticmethod
    def _format(partition):
        if "efi" in partition.mountpoint:
            cmd = f"mkfs.vfat {_options(partition)} %s"
        elif partition.mountpoint == "/boot":
            cmd = f"mkfs.ext2 {_options(partition)} %s"
        elif partition.mountpoint == "swap":
            cmd = f"mkswap {_options(partition)} %s"
        elif partition.fs:
            cmd = f"mkfs.{partition.fs} {_options(partition)} %s"
        else:
            cmd = f"mkfs.ext4 {_options(partition)} %s"

        SpawnedSU.do(cmd % partition.url)

        if partition.fs == "btrfs" and partition.subvolumes:
            root = "/mnt"
            SpawnedSU.do(f"mount -o compress=lzo {partition.url} {root}")
            for subv, mpoint in partition.subvolumes.items():
                SpawnedSU.do(f"mkdir -p {root}{mpoint} && btrfs subvolume create {root}/{subv}")
            SpawnedSU.do(f"umount {partition.url}")

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
