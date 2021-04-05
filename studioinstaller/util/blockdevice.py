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
#  Copyright (c) 2021 remico

from spawned import SpawnedSU, Spawned

__all__ = [
    'solid',
    'discardable',
    'uuid',
    'test_luks_key',
    'boot_partition',
    'root_partition',
]


def solid(volume_url):
    return Spawned.do(f"lsblk -n -d -o ROTA {volume_url}").strip() == "0"  # 0 - SSD, 1 - HDD


def discardable(partition):
    pattern = "TRIM supported"
    return solid(partition.url) and \
        pattern in SpawnedSU.do(f'sudo hdparm -I {partition.disk} | grep "{pattern}"')


def uuid(volume_url):
    return SpawnedSU.do(f"blkid -s UUID -o value {volume_url}")


def test_luks_key(volume_url, key):
    return SpawnedSU.do(
            f"cryptsetup open --test-passphrase -d {key} {volume_url} 2>/dev/null",
            with_status=True
        ).success


def boot_partition(scheme):
    for pt in scheme:
        if pt.mountpoint == "/boot":
            return pt
    return root_partition(scheme)


def root_partition(scheme):
    for pt in scheme:
        if pt.mountpoint == "/":
            return pt


# TODO lsblk -o name,type,path,mountpoint,rota,uuid,disc-gran,disc-max,label,partlabel --json /dev/sd*
# -l -n -p -I <major_num>
