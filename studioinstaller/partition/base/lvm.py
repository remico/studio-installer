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

""" Partitions hierarchy """

from .partitionbase import Partition
from ...spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

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
