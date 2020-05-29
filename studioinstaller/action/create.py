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

"""Create partition action"""

from .actionbase import ActionBase
from .encrypt import Encrypt
from ..partition.base import PV
from ..spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Create']


class Create(ActionBase):
    def __next__(self):
        for p in self.nodes:
            while p and p.parent in self.nodes:
                p = p.parent
            self.nodes.remove(p)
            return p
        raise StopIteration

    def iterator(self, scheme):
        self.nodes = scheme.disks()

        # sort PVs first
        # filter: PVs, to be created only
        pvs = scheme.partitions(PV, new=True)
        # URL is valid key for sorting PVs
        self.nodes.extend(sorted(pvs, key=lambda p: p.url))

        # then sort non-PVs
        def _k(p):
            if p.iscontainer:  # LUKS, LVM ? (TODO: luks_on_lvm first, then lvm_on_luks)
                return 0
            if p.mountpoint == "/":
                return 1
            elif p.isswap:
                return 2
            else:
                return 3 + len(p.mountpoint.split('/'))

        # filter: non-PVs, to be created only
        non_pvs = [pt for pt in scheme if not isinstance(pt, PV) and pt.is_new]
        self.nodes.extend(sorted(non_pvs, key=_k))

        return self

    def serve_disk(self, disk):
        disk.create_new_partition_table()

    def serve_standard_pv(self, pt):
        pt.create()

    def serve_luks_pv(self, pt):
        pt.create()
        pt.execute(Encrypt())

    def serve_lvm_on_luks_vg(self, pt):
        pt.luks_open()
        pt.init_vg()

    def serve_lvm_lv(self, pt):
        assert pt.lvm_vg, "No LVM VG is defined for an LVM LV. Abort."
        l_option = "-l" if "%" in pt.size else "-L"
        SpawnedSU.do(f"lvcreate {l_option} {pt.size} {pt.lvm_vg} -n {pt.lvm_lv}")
