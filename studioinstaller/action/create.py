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

"""Create a partition:
- create a standard partition
- create and encrypt a LUKS partition
- register PV and VG for an LVM group
- create an LVM LV
"""

import re
from spawned import SpawnedSU, Spawned

from .actionbase import ActionBase, _sort_key
from .encrypt import Encrypt
from .involve import Involve
from ..partition.base import PV

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

    def _create(self, partition):
        if not partition.is_new:
            return

        # extract numeric ID value from the whole id value (e.g. '1' from 'sda1')
        partition_id = re.search(r"(\d*)$", partition.id).group()

        basic_prompt = "Command (? for help)"

        t = SpawnedSU(f"gdisk {partition.disk}")

        t.interact(basic_prompt, "n")
        t.interact("Partition number", partition_id or Spawned.ANSWER_DEFAULT)
        t.interact("First sector", Spawned.ANSWER_DEFAULT)
        t.interact("Last sector", f"+{partition.size}" if partition.size else Spawned.ANSWER_DEFAULT)
        t.interact("Hex code or GUID", partition.type or Spawned.ANSWER_DEFAULT)

        # add partition label
        if partition_id and partition.label:
            t.interact(basic_prompt, "c")

            if label_prefix := self._extra_kw.get('system_label'):
                partition_label = label_prefix + '-' + partition.label
            else:
                partition_label = partition.label

            while 0 != t.interact(("Enter name", partition_label),
                                  ("Partition number", partition_id)):
                continue

        t.interact(basic_prompt, "w")
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
