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

from abc import abstractmethod
from enum import Enum
from typing import final

from spawned import SpawnedSU

from .mediumbase import MediumBase, URL_MAPPED, URL_PV, URL_DISK, URL_LVM_LV

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Partition', 'VType']


class VType(Enum):
    DEFAULT = ""
    EFI = "ef00"
    SWAP = "8200"
    LUKS = "8309"
    LINUXFS = "8300"
    HOME = "8302"
    LINUXLVM = "8e00"

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()


_M = "mapper"
_D = ":"


class Partition(MediumBase):
    MAX_SIZE = ''

    """Base class for all supported partition types"""
    @abstractmethod
    def __init__(self, mountpoint='', vg='', lv='', **kwargs):
        super().__init__(**kwargs)

        self.is_new = False
        self.do_format = False
        self.size = ''
        self.type = str(VType.DEFAULT)
        self.fs = ''

        self.lvm_vg = vg
        self.lvm_lv = lv

        self.mountpoint = mountpoint

    def new(self, size=MAX_SIZE, type_=VType.DEFAULT):
        """Create a new partition"""
        self.is_new = True
        self.size = size
        self.type = str(type_)
        return self

    @final
    def execute(self, action):
        print(f">>>>> ACTION [{action.__class__.__name__}]:", f"<{self.__class__.__name__}>::{self.id}")
        self._a_execute(action)

    @abstractmethod
    def _a_execute(self, action):
        pass

    @property
    def isphysical(self):
        """A real partition on the physical drive (e.g. /dev/sda1)"""
        return False

    @property
    def iscontainer(self):
        """Not a top level partition.
        An encrypted partition or an LVM PV:
            - LUKS on /dev/sda1
            - LVM VG on /dev/sda1
            - LVM VG on /dev/mapper/crypt_lvm
        """
        return False

    @property
    def islvm(self):
        """Partition belongs to an LVM volume group"""
        return bool(self.lvm_vg and self.lvm_lv)

    @property
    def disk(self):
        """Valid for physical partitions only"""
        return URL_DISK(self.parent.id) if self.isphysical and self.parent else ''

    @property
    def mapperID(self):
        """Actual ID of a device in /dev/mapper/ directory"""
        return self.id if not self.isphysical else ''

    @property
    def url(self):
        """Path to the device in file system"""
        return URL_PV(self.id) if self.isphysical else \
            URL_LVM_LV(self.lvm_vg, self.lvm_lv) if self.islvm else URL_MAPPED(self.id)

    @property
    def isswap(self):
        """SWAP partition"""
        return self.mountpoint == 'swap'

    @property
    def isspecial(self):
        """Not a regular partition, actually a SWAP or EFI partition"""
        return self.isswap or 'efi' in self.mountpoint

    @property
    def uuid(self):
        """Partition UUID.
        A luks partition must be open before, otherwise uuid is empty.
        """
        return SpawnedSU.do(f"blkid -s UUID -o value {self.url}")
