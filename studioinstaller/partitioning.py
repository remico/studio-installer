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

"""Partitioning scheme"""

from .partition.base import VType, LuksType
from .partition import Disk, PlainPV, LuksPV, LvmOnLuksVG, LvmLV, CryptVV
from .scheme import Scheme

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"


# edit partitioning configuration according to your needs
def scheme(target_disk: Disk):
    disk1 = Disk(target_disk)

    p1 = PlainPV(1, '/boot/efi').new('200M', VType.EFI).on(disk1).makefs()

    p2 = LuksPV(2, type=LuksType.luks1).new('500M').on(disk1)
    boot = CryptVV('boot', '/boot').new().on(p2).makefs('ext2')

    p3 = LuksPV(3).new().on(disk1)
    lvm_vg = LvmOnLuksVG('studio-vg', 'CRYPTLVM').new().on(p3)

    root = LvmLV('root', '/').new('30G').on(lvm_vg).makefs('ext4')
    swap = LvmLV('swap', 'swap').new('13G', VType.SWAP).on(lvm_vg)
    data = LvmLV('data', '/media/studio-data').new('30G').on(lvm_vg).makefs('ext4')
    home = LvmLV('home', '/home').new(LvmLV.MAX_SIZE).on(lvm_vg).makefs('ext4')

    return Scheme([p1, p2, p3, lvm_vg, boot, root, home, swap, data])
