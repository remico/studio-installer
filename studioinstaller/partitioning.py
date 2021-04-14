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

# TODO: fill scheme dynamically

# edit partitioning configuration according to your needs
def scheme(target_disk: str, scheme_id):
    disk1 = Disk(target_disk)

    if not scheme_id:
        p1 = PVPlain(1, '/boot/efi').new('200M', VType.EFI, "efi").on(disk1).makefs()

        p2 = PVLuks(2, type=LuksType.luks1).new('500M', label="boot").on(disk1)
        boot = VVCrypt('boot', '/boot').new(label="BOOT").on(p2).makefs('ext2')

        p3 = PVLuks(3).new(label="lvm").on(disk1)
        lvm_vg = VGLvmOnLuks('studio-vg', 'CRYPTLVM').new().on(p3)  # FIXME: replace hardcoded <studio>

        root = LVLvm('root', '/').new('40G', label='ROOTFS').on(lvm_vg).makefs('btrfs', subvolumes={'@': '/', '@cache': '/var/cache'})
        swap = LVLvm('swap', 'swap').new('14G', VType.SWAP, label="SWAP").on(lvm_vg)
        # data = LVLvm('data', '/media/studio-data').new('30G', label="DATA").on(lvm_vg).makefs('ext4')
        home = LVLvm('home', '/home').new(LVLvm.MAX_SIZE, label="HOME").on(lvm_vg).makefs('btrfs', subvolumes={'@home': '/home'})

        return Scheme([p1, p2, p3, lvm_vg, boot, root, home, swap, ])

    elif scheme_id == 1:
        efi = PVPlain(1, '/boot/efi').new('200M', VType.EFI, "efi").on(disk1).makefs()
        root = PVPlain(2, '/').new('10G', label='ROOTFS').on(disk1).makefs('btrfs', subvolumes={'@': '/'})
        swap = PVPlain(3, 'swap').new('9G', VType.SWAP, label="SWAP").on(disk1)
        home = PVPlain(4, '/home').new(label="HOME").on(disk1).makefs('btrfs', subvolumes={'@home': '/home'})
        return Scheme([efi, root, home, swap])
