#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Create partition action """

__author__ = 'remico <remicollab@gmail.com>'

from .actionbase import ActionBase
from ..partition.base import PV

__all__ = ['Create']


class Create(ActionBase):
    def iterator(self, scheme):
        # include disks (aka PVs' parents) first
        disks = [pv.parent for pv in scheme.partitions(PV)]
        # filter only partitions to be created
        disks.extend([pt for pt in scheme if pt.is_new])
        return disks.__iter__()

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
        pt.create()
        # if pt.do_format or pt.isswap:
        #     pt.format()
