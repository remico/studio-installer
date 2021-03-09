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

from abc import abstractclassmethod, ABC

from spawned import SpawnedSU

from ..action import Involve, Release

__all__ = ['PostInstaller']


class PostInstaller(ABC):
    def __init__(self, scheme, op) -> None:
        self.scheme = scheme
        self.op = op

    def execute(self):
        self._run()

    def mount_target_system(self):
        SpawnedSU.do(f"mkdir -p {self.chroot}")
        self.scheme.execute(Involve(chroot=self.chroot))

        SpawnedSU.do(f"""
            for n in sys dev etc/resolv.conf; do
                mount --bind /$n {self.chroot}/$n;
            done
            mount -t proc none {self.chroot}/proc
            mount -t devpts devpts {self.chroot}/dev/pts
            """)

    def unmount_target_system(self):
        SpawnedSU.do(f"""
            for n in dev/pts dev proc sys etc/resolv.conf; do
                umount {self.chroot}/$n;
            done
            """)

        self.scheme.execute(Release())

    @abstractclassmethod
    def _run(self):
        pass

    @abstractclassmethod
    def inject_tool(self, extras=False, develop=False):
        pass
