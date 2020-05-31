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

"""Release an unnecessary partition:
- unmount a regular partition
- close a LUKS device
- deactivate a SWAP partition
- deactivate all LMV LVs in an LVM VG
"""

from spawned import SpawnedSU
from .actionbase import ActionBase, _sort_key

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Release']


class Release(ActionBase):
    def __next__(self):
        return super().__next__()

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
        if not partition.isswap:
            SpawnedSU.do(f"umount {partition.url}")
        else:
            SpawnedSU.do(f"swapoff {partition.url}")

    def serve_standard_pv(self, pt):
        self._umount(pt)

    def serve_luks_pv(self, pt, mapper_id=None):
        self._luks_close(pt, mapper_id)

    def serve_lvm_on_luks_vg(self, pt):
        SpawnedSU.do(f"vgchange -a n {pt.lvm_vg}")

    def serve_lvm_lv(self, pt):
        self._umount(pt)
