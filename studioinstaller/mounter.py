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

from spawned import SpawnedSU

from .action import Involve, Release

__all__ = ['Mounter']


class Mounter:
    def __init__(self, chroot, scheme) -> None:
        self.chroot = chroot
        self.scheme = scheme

    def mount_target_system(self):
        SpawnedSU.do(f"mkdir -p {self.chroot}")
        self.scheme.execute(Involve(chroot=self.chroot))

        SpawnedSU.do(f"""
            for n in sys proc dev etc/resolv.conf sys/firmware/efi/efivars; do
                mount --bind /$n {self.chroot}/$n;
            done
            mount -t devpts devpts {self.chroot}/dev/pts
            """)

    def unmount_target_system(self):
        mounts = SpawnedSU.do(f'mount | grep "{self.chroot}" | cut -d" " -f3', list_=True)
        mounts.reverse()

        for m in mounts:
            SpawnedSU.do(f"umount {m}")

        self.scheme.execute(Release())
