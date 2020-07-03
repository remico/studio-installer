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

"""Create a partition:
- create a standard partition
- create and encrypt a LUKS partition
- register PV and VG for an LVM group
- create an LVM LV
"""

from spawned import SpawnedSU, Spawned

from .actionbase import ActionBase, _sort_key
from .encrypt import Encrypt
from .involve import Involve
from ..partition.base import PV

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
        # sort PVs first
        pvs = scheme.partitions(PV)
        # URL is valid key for sorting PVs
        self.nodes.extend(sorted(pvs, key=lambda p: p.url))

        # then sort non-PVs
        non_pvs = [pt for pt in scheme if not isinstance(pt, PV)]
        non_pvs = sorted(non_pvs, key=_sort_key)

        # place relative-sized partition at the end of the list
        def _sort_key_2(pt):
            return 1 if "100%FREE" in pt.size else 0  # warning: magic value

        self.nodes.extend(sorted(non_pvs, key=_sort_key_2))

        return self

    @staticmethod
    def _create(partition, t: Spawned = None):
        if not partition.is_new:
            return

        locally = not t
        if locally:
            t = SpawnedSU(f"gdisk {partition.disk}")

        # extract numeric ID value from the actual id (e.g. '1' from 'sda1')
        partition_id = ''.join([ch for ch in partition.id if ch.isdigit()])

        basic_prompt = "Command (? for help)"
        t.interact(basic_prompt, "n")
        t.interact("Partition number", partition_id or Spawned.ANSWER_DEFAULT)
        t.interact("First sector", Spawned.ANSWER_DEFAULT)
        t.interact("Last sector", f"+{partition.size}" if partition.size else Spawned.ANSWER_DEFAULT)
        t.interact("Hex code or GUID", partition.type or Spawned.ANSWER_DEFAULT)

        # add partition label
        if partition_id and partition.label:
            t.interact("Command (? for help)", "c")

            q_0 = "Partition number"
            a_0 = partition_id
            q_1 = "Enter name"
            a_1 = "studio-" + partition.label

            idx = t.interact([q_0, q_1],
                             [a_0, a_1])
            if idx == 0:
                t.interact(q_1, a_1)

        if locally:
            t.interact("Command (? for help)", "w")
            t.interact("proceed?", "Y")
            t.waitfor(Spawned.TASK_END)

    def serve_standard_pv(self, pt):
        self._create(pt)

    def serve_luks_pv(self, pt):
        self._create(pt)
        pt.execute(Encrypt())

    def serve_lvm_on_luks_vg(self, pt):
        pt.parent.execute(Involve())
        SpawnedSU.do(f"pvcreate {pt.url} && vgcreate {pt.lvm_vg} {pt.url}")

    def serve_lvm_lv(self, pt):
        assert pt.lvm_vg, f"No LVM VG is defined for LVM LV {pt.id}. Abort."
        l_option = "-l" if "%" in pt.size else "-L"
        SpawnedSU.do(f"lvcreate {l_option} {pt.size} {pt.lvm_vg} -n {pt.lvm_lv}")

    def serve_encrypted_vv(self, pt):
        pt.parent.execute(Involve())
