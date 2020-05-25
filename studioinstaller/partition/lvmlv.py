#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import FS, LVM_ID, LVM
from .lvmpv import LvmPV

__all__ = ['LvmLV']


class LvmLV(FS, LVM):
    def __init__(self, lv, mountpoint=''):
        super().__init__(id_='', lv=lv, mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_lvm_lv(self)

    def on(self, parent: LvmPV):
        self.lvm_vg = parent.lvm_vg
        self._id = LVM_ID(parent.lvm_vg, self.lvm_lv)
        return super().on(parent)

    @staticmethod
    def groups(scheme):
        return set([pt.lvm_vg for pt in scheme if isinstance(pt, LvmLV)])
