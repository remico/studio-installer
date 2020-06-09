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

"""Encrypt partition using cryptsetup"""

from spawned import SpawnedSU

from .actionbase import ActionBase
from ..partition.base import LUKS

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

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
