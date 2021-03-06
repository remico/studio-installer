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

"""Partitioning scheme"""

from .partition.base import VType, LuksType
from .partition import Disk, PVPlain, PVLuks, VGLvmOnLuks, LVLvm, VVCrypt
from .scheme import Scheme


# edit partitioning configuration according to your needs
def scheme(target_disk: str):
    disk1 = Disk(target_disk)

    p1 = PVPlain(1, '/boot/efi').new('200M', VType.EFI, "EFI").on(disk1).makefs()

    p2 = PVLuks(2, type=LuksType.luks1).new('500M', label="boot").on(disk1)
    boot = VVCrypt('boot', '/boot').new().on(p2).makefs('ext2')

    p3 = PVLuks(3).new(label="lvm-all").on(disk1)
    lvm_vg = VGLvmOnLuks('studio-vg', 'CRYPTLVM').new().on(p3)

    root = LVLvm('root', '/').new('30G').on(lvm_vg).makefs('ext4')
    swap = LVLvm('swap', 'swap').new('13G', VType.SWAP).on(lvm_vg)
    data = LVLvm('data', '/media/studio-data').new('30G').on(lvm_vg).makefs('ext4')
    home = LVLvm('home', '/home').new(LVLvm.MAX_SIZE).on(lvm_vg).makefs('ext4')

    return Scheme([p1, p2, p3, lvm_vg, boot, root, home, swap, data])
