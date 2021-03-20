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

from spawned import ChrootContext, SpawnedSU

from ..postinstaller import PostInstaller
from ... import util

__all__ = ['ManjaroPostInstaller']


class ManjaroPostInstaller(PostInstaller):
    def _run(self):
        self.mounter.mount_target_system()

        with ChrootContext(self.op.chroot) as cntx:
            setup_bootloader(cntx, self.disk, grub_id=self.op.L, cryptoboot=True)
            setup_kernel_parameters(cntx)
            setup_encryption(cntx)

        self.mounter.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mounter.mount_target_system()

        # install the tool into the target OS

        self.mounter.unmount_target_system()


def setup_bootloader(cntx, grub_disk, grub_id=None, cryptoboot=False):

    # FIXME: replace hardcoded /dev/sda3 and CRYPTLVM with the value found in runtime
    root_pv_uuid = SpawnedSU.do(f"blkid -o value -s UUID /dev/sda3")
    root_lvm_pv = "CRYPTLVM"

    grub_crypt_commands = rf"""
                        FILE=/etc/default/grub

                        grep "GRUB_ENABLE_CRYPTODISK=y" $FILE \
                        && sed -i s/^#GRUB_ENABLE_CRYPTODISK=y/GRUB_ENABLE_CRYPTODISK=y/ $FILE \
                        || echo "GRUB_ENABLE_CRYPTODISK=y" >> $FILE

                        sed -i s,GRUB_CMDLINE_LINUX=\",GRUB_CMDLINE_LINUX=\"cryptdevice=UUID={root_pv_uuid}:{root_lvm_pv}:allow-discards\ , $FILE
                        """
    enable_grub_crypt = grub_crypt_commands if cryptoboot else ""

    if util.is_efi_boot():
        grub_install = f"grub-install --recheck --efi-directory=/boot/efi --bootloader-id={grub_id} --boot-directory=/boot"
    else:
        grub_install = f"grub-install --recheck --boot-directory=/boot {grub_disk}"

    cntx.do(f"""
        pacman --noconfirm -S grub
        {enable_grub_crypt}
        {grub_install}
        update-grub
        """)


def setup_kernel_parameters(cntx):
    # FIXME: check in runtime if btrfs is used
    btrfs_root = "rootflags=subvol=@"  # FIXME: replace hardcoded @ with the value found in runtime

    # cntx.do(f"""
    #     sed -i s,GRUB_CMDLINE_LINUX=",GRUB_CMDLINE_LINUX="{btrfs_root} , /etc/boot/grub
    #     """)


def setup_encryption(cntx):
    # FIXME: replace hardcoded /dev/sda{2,3} with the value found in runtime
    boot_pv_uuid = SpawnedSU.do(f"blkid -o value -s UUID /dev/sda2")
    root_pv_uuid = SpawnedSU.do(f"blkid -o value -s UUID /dev/sda3")

    cntx.do(f"""
        echo "boot       UUID={boot_pv_uuid}     none    luks,discard" >> /etc/crypttab
        echo "# CRYPTLVM   UUID={root_pv_uuid}     none    luks,discard" >> /etc/crypttab
        mkinitcpio -P
        """)
