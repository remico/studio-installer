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

""" Create partition action """

from .actionbase import ActionBase
from ..partition.base import PV
from ..spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Create']


class Create(ActionBase):
    def iterator(self, scheme):
        # include disks (aka PVs' parents) first; avoid duplications
        to_iter = list({pv.parent for pv in scheme.partitions(PV)})
        # filter only partitions to be created
        to_iter.extend([pt for pt in scheme if pt.is_new])
        return to_iter.__iter__()

    def serve_disk(self, disk):
        disk.create_new_partition_table()

    def serve_standard_pv(self, pt):
        pt.create()
        # if pt.do_format:
        #     pt.format()

    def serve_luks_pv(self, pt):
        pt.create()
        # pt.encrypt()

    def serve_lvm_on_luks_vg(self, pt):
        pt.luks_open()
        pt.init_vg()

    def serve_lvm_lv(self, pt):
        assert pt.lvm_vg, "No LVM VG is defined for an LVM LV. Abort."
        l_option = "-l" if "%" in pt.size else "-L"
        SpawnedSU.do(f"lvcreate {l_option} {pt.size} {pt.lvm_vg} -n {pt.lvm_lv}")
        # if pt.do_format or pt.isswap:
        #     pt.format()
