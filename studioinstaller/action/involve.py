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

"""Involve a partition to be used:
- mount a regular partition
- open a LUKS device
- activate a SWAP partition
- activate an LVM VG
"""

from pathlib import Path
from spawned import SpawnedSU
from .actionbase import ActionBase, _sort_key

__all__ = ['Involve']


class Involve(ActionBase):
    def iterator(self, scheme):
        self.nodes.extend(sorted(scheme.partitions(), key=_sort_key))
        return self

    @staticmethod
    def _luks_open(partition, passphrase=None, mapper_id=None):
        name_to_open = partition.mapperID or mapper_id
        assert name_to_open, f"Is it LUKS? 'mapperID' is not defined for {partition.id}"
        if passphrase:
            partition._passphrase = passphrase
        with SpawnedSU(f"cryptsetup open {partition.url} {name_to_open}") as t:
            t.interact("Enter passphrase for", partition.passphrase)

    @staticmethod
    def _mount(partition, chroot, mountpoint=None, mount_options=''):
        if partition.isswap:
            SpawnedSU.do(f"swapon {partition.url}")

        else:
            assert chroot, f"No 'chroot' defined while trying to mount '{partition.id}'"
            mpoint = mountpoint or partition.mountpoint

            if not mpoint:  # prevent incorrect mounting to chroot's '/'
                return

            # note: if Path() gets several absolute paths, the last one is taken as an anchor
            #  so we need to strip the leading '/' from the second path
            # TODO: find a better way to concatenate 2 absolute paths
            if mpoint.startswith('/'):
                mpoint = mpoint.lstrip('/')
            mpoint = Path(chroot, mpoint)

            SpawnedSU.do(f"mkdir -p {mpoint}")
            SpawnedSU.do(f"mount {mount_options} {partition.url} {mpoint}")

    def serve_standard_pv(self, pt, mountpoint=None, chroot=None):
        chroot = chroot or self._extra_kw.get('chroot')
        mountpoint = mountpoint or self._extra_kw.get('mountpoint')

        if pt.fs == "btrfs":
            if pt.subvolumes:
                for subv, mpoint in pt.subvolumes.items():
                    self._mount(pt, chroot, mpoint, mount_options=f"-o compress=lzo,subvol={subv}")
            else:
                self._mount(pt, chroot, mountpoint, mount_options="-o compress=lzo")
        else:
            self._mount(pt, chroot, mountpoint)

    def serve_luks_pv(self, pt, passphrase=None, mapper_id=None):
        passphrase = passphrase or self._extra_kw.get('passphrase')
        mapper_id = mapper_id or self._extra_kw.get('mapper_id')
        self._luks_open(pt, passphrase, mapper_id)

    def serve_lvm_on_luks_vg(self, pt):
        SpawnedSU.do(f"sudo vgchange -ay {pt.lvm_vg}")

    def serve_lvm_lv(self, pt, mountpoint=None, chroot=None):
        self.serve_standard_pv(pt, mountpoint, chroot)

    def serve_encrypted_vv(self, pt, mountpoint=None, chroot=None):
        self.serve_standard_pv(pt, mountpoint, chroot)
