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

"""Encrypt partition using cryptsetup"""

from spawned import SpawnedSU

from .actionbase import ActionBase
from ..partition.base import LUKS

__all__ = ['Encrypt']


class Encrypt(ActionBase):
    def iterator(self, scheme):
        self.nodes.extend([pt for pt in scheme.partitions(LUKS)])
        return self

    @staticmethod
    def _encrypt(partition, passphrase=None):
        assert isinstance(partition, LUKS), f"Partition {partition.id} doesn't look like a LUKS volume"
        if passphrase:
            partition._passphrase = passphrase
        with SpawnedSU(f"cryptsetup luksFormat --type={partition.luks_type} {partition.url}") as t:
            t.interact("Type uppercase yes", "YES")
            t.interact("Enter passphrase for", partition.passphrase)
            t.interact("Verify passphrase", partition.passphrase)

    def serve_standard_pv(self, pt):
        pass

    def serve_luks_pv(self, pt):
        self._encrypt(pt)

    def serve_lvm_on_luks_vg(self, pt):
        pass

    def serve_lvm_lv(self, pt):
        pass

    def serve_encrypted_vv(self, pt):
        pass
