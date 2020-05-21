#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import FS, LVM_ID, LVM
from .lvmpv import LvmPV
from ..spawned import SpawnedSU

__all__ = ['LvmLV']


class LvmLV(FS, LVM):
    def __init__(self, lv, mountpoint=''):
        super().__init__(id_='', lv=lv, mountpoint=mountpoint)

    def create(self):
        l_option = "-l" if "%" in self.size else "-L"
        SpawnedSU.do(f"lvcreate {l_option} {self.size} {self.lvm_vg} -n {self.lvm_lv}")

    def do_serve(self):
        assert self.lvm_vg, "No LVM VG is defined for an LVM LV. Abort."
        if self.is_new:
            self.create()
        if self.do_format or self.isswap:
            self.format()

    def on(self, parent: LvmPV):
        self.lvm_vg = parent.lvm_vg
        self._id = LVM_ID(parent.lvm_vg, self.lvm_lv)
        return super().on(parent)

    @staticmethod
    def groups(scheme):
        return set([pt.lvm_vg for pt in scheme if isinstance(pt, LvmLV)])
