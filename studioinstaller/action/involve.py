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

"""Involve a partition to be used:
- mount a regular partition
- open a LUKS device
- activate a SWAP partition
- activate an LVM VG
"""

from spawned import SpawnedSU
from .actionbase import ActionBase

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Involve']


class Involve(ActionBase):
    def __next__(self):
        # impl
        raise StopIteration

    def iterator(self, scheme):
        # impl
        return self

    @staticmethod
    def _luks_open(partition, passphrase=None, mapper_id=None):
        assert partition.mapperID or mapper_id, f"Is it LUKS? 'mapperID' is not defined for {partition.id}"
        if passphrase:
            partition._passphrase = passphrase
        with SpawnedSU(f"cryptsetup open {partition.luks_url} {partition.mapperID or mapper_id}") as t:
            t.interact("Enter passphrase for", partition.passphrase)

    @staticmethod
    def _mount(partition, chroot=None):
        mountpoint = chroot or partition.mountpoint
        if mountpoint and not partition.isswap:
            SpawnedSU.do(f"mount {partition.url} {mountpoint}")
        elif partition.isswap:
            SpawnedSU.do(f"swapon {partition.url}")

    def serve_standard_pv(self, pt, chroot=None):
        self._mount(pt, chroot)

    def serve_luks_pv(self, pt, passphrase=None, mapper_id=None):
        self._luks_open(pt, passphrase, mapper_id)

    def serve_lvm_on_luks_vg(self, pt):
        SpawnedSU.do(f"sudo vgchange -ay {pt.lvm_vg}")

    def serve_lvm_lv(self, pt, chroot=None):
        self._mount(pt, chroot)
