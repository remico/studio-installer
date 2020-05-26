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

from os import getenv as ENV
from .partitionbase import Partition
from ...spawned import SpawnedSU, ask_user

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['LUKS']


class LUKS(Partition):
    def __init__(self, passphrase=None, **kwargs):
        self._passphrase = passphrase
        super().__init__(**kwargs)

    @property
    def passphrase(self):
        # FIXME remove checking for user
        if not self._passphrase and ENV('USER') != 'user':
            self._passphrase = ask_user("Enter LUKS passphrase:")
        return self._passphrase

    @property
    def _luks_volume(self):
        return self.url if self.isphysical or (self.islvm and not self.iscontainer) else self.parent.url

    def luks_open(self, passphrase=None, mapper_id=None):
        assert self.mapperID or mapper_id, "mapperID is not defined for this partition"
        if passphrase:
            self._passphrase = passphrase
        with SpawnedSU(f"cryptsetup open {self._luks_volume} {self.mapperID or mapper_id}") as t:
            t.interact("Enter passphrase for", self.passphrase)

    def luks_close(self, mapper_id=None):
        assert self.mapperID or mapper_id, "mapperID is not defined for this partition"
        SpawnedSU.do(f"cryptsetup close {self.mapperID or mapper_id}")
