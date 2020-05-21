#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .partitionbase import Partition
from ...spawned import SpawnedSU

__all__ = ['LVM', 'LVM_ID']


def LVM_ID(vg, lv):
    return f"{vg}-{lv}"


class LVM(Partition):
    @property
    def islvm(self):
        return True

    def init_vg(self):
        SpawnedSU.do(f"pvcreate {self.url}")
        SpawnedSU.do(f"vgcreate {self.lvm_vg} {self.url}")
