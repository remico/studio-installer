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

"""Release an unnecessary partition:
- unmount a regular partition
- close a LUKS device
- deactivate a SWAP partition
- deactivate all LMV LVs in an LVM VG
"""

from spawned import SpawnedSU
from .actionbase import ActionBase, _sort_key

__all__ = ['Release']


class Release(ActionBase):
    def iterator(self, scheme):
        self.nodes.extend(sorted(scheme.partitions(), key=_sort_key, reverse=True))
        return self

    @staticmethod
    def _luks_close(partition, mapper_id=None):
        name_to_close = partition.mapperID or mapper_id
        assert name_to_close, f"Is it LUKS? 'mapperID' is not defined for {partition.id}"
        SpawnedSU.do(f"cryptsetup close {name_to_close}")

    @staticmethod
    def _umount(partition):
        if partition.isswap:
            SpawnedSU.do(f"swapoff {partition.url}")
        else:
            SpawnedSU.do(f"umount {partition.url}")

    def serve_standard_pv(self, pt):
        self._umount(pt)

    def serve_luks_pv(self, pt, mapper_id=None):
        mapper_id = mapper_id or self._extra_kw.get('mapper_id')
        self._luks_close(pt, mapper_id)

    def serve_lvm_on_luks_vg(self, pt):
        SpawnedSU.do(f"vgchange -a n {pt.lvm_vg}")

    def serve_lvm_lv(self, pt):
        self._umount(pt)

    def serve_encrypted_vv(self, pt):
        self._umount(pt)
