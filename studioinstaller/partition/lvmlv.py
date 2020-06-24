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

"""Partitions hierarchy"""

from .base import FS, VType
from .lvmpv import LvmPV

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['LvmLV']


class LvmLV(FS):
    MAX_SIZE = '100%FREE'

    def __init__(self, lv, mountpoint=''):
        super().__init__(id_=lv, lv=lv, mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_lvm_lv(self)

    def new(self, size=MAX_SIZE, type_=VType.DEFAULT):
        return super().new(size, type_)

    def on(self, parent: LvmPV):
        self.lvm_vg = parent.lvm_vg
        return super().on(parent)

    @staticmethod
    def groups(scheme):
        return set([pt.lvm_vg for pt in scheme if isinstance(pt, LvmLV)])
