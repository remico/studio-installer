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

from .base import PV, Container, LUKS
from ..spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['LuksPV']


class LuksPV(LUKS, PV, Container):
    def __init__(self, id_):
        super().__init__(id_=str(id_))

    def encrypt(self, passphrase=None):
        if passphrase:
            self._passphrase = passphrase
        with SpawnedSU(f"cryptsetup luksFormat {self.url}") as t:
            t.interact("Type uppercase yes", "YES")
            t.interact("Enter passphrase for", self.passphrase)
            t.interact("Verify passphrase", self.passphrase)

    def _a_execute(self, action):
        action.serve_luks_pv(self)
