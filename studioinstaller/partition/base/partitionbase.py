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

from abc import abstractmethod
from typing import final

from _typing import StringEnum

from .mediumbase import MediumBase, URL_MAPPED, URL_PV, URL_DISK, URL_LVM_LV
from ...util import volume_uuid

__all__ = ['Partition', 'VType']


class VType(StringEnum):
    DEFAULT = ""
    GRUB_BIOS_BOOT = "ef02"
    EFI = "ef00"
    SWAP = "8200"
    LUKS = "8309"
    LINUXFS = "8300"
    HOME = "8302"
    LINUXLVM = "8e00"


_M = "mapper"
_D = ":"

# possible partitions distinction by url
# Plain: len(url) == 2 + 'mapper' not in url
# LVM LV: len(url) > 2 + 'mapper' not in url
# LVM VG: ? (not Plain + not LVM LV + not LUKS)
# LUKS: len(url) > 2 + 'mapper' in url


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
        self.subvolumes = {}
        self.label = ''

        self.lvm_vg = vg
        self.lvm_lv = lv

        self.mountpoint = mountpoint

    def new(self, size=MAX_SIZE, type_=VType.DEFAULT, label=""):
        """Create a new partition"""
        self.is_new = True
        self.size = size
        self.type = str(type_)
        self.label = label
        return self

    def on(self, parent):
        self._parent = parent
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
        """Non-FS partition.
        An encrypted partition or an LVM PV:
            - LUKS on /dev/sda1
            - LVM VG on /dev/sda1
            - LVM VG on /dev/mapper/crypt_lvm
        """
        return False

    @property
    def islvmlv(self):
        """Partition is an LVM logical volume"""
        return bool(self.lvm_vg and self.lvm_lv)

    @property
    def disk(self):
        p = self
        while p.parent:
            p = p.parent
        return URL_DISK(p.id)

    @property
    def mapperID(self):
        """Actual ID of a device in /dev/mapper/ directory"""
        return self.id if not self.isphysical else ''

    @property
    def url(self):
        """Path to the device in file system"""
        return URL_PV(self.id) if self.isphysical else \
            URL_LVM_LV(self.lvm_vg, self.lvm_lv) if self.islvmlv else URL_MAPPED(self.id)

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
        return volume_uuid(self.url)
