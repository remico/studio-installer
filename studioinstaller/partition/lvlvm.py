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

"""Partitions hierarchy"""

from .base import FS, VType
from .pvlvm import PVLvm

__all__ = ['LVLvm']


class LVLvm(FS):
    MAX_SIZE = '100%FREE'

    def __init__(self, lv, mountpoint=''):
        super().__init__(id_=lv, lv=lv, mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_lvm_lv(self)

    def new(self, size=MAX_SIZE, type_=VType.DEFAULT, label=""):
        return super().new(size, type_, label)

    def on(self, parent: PVLvm):
        self.lvm_vg = parent.lvm_vg
        return super().on(parent)

    @staticmethod
    def groups(scheme):
        return set([pt.lvm_vg for pt in scheme if isinstance(pt, LVLvm)])
