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

from spawned import ChrootContext, ENV, Spawned

from ..postinstaller import PostInstaller

__all__ = ['ManjaroPostInstaller']


class ManjaroPostInstaller(PostInstaller):
    def _run(self):
        self.mounter.mount_target_system()

        with ChrootContext(self.chroot, self.disk, grub_id="studio") as cntx:
            setup_bootloader(cntx)

        self.mounter.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mounter.mount_target_system()

        # install the tool into the target OS

        self.mounter.unmount_target_system()

def setup_bootloader(cntx, grub_disk, grub_id=None, cryptoboot=False):
    cntx.do(f"""
    pacman -S grub
    sed -i s/^#GRUB_ENABLE_CRYPTODISK=y/GRUB_ENABLE_CRYPTODISK=y/ /etc/default/grub
    grub-install --recheck --efi-directory=/boot/efi {grub_disk}
    update-grub
    """)
