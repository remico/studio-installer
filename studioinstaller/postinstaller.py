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

"""Post-installation setup"""

from spawned import SpawnedSU, Chroot

from .action import Involve, Release
from .scheme import Scheme

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PostInstaller']


class PostInstaller:
    def __init__(self, scheme: Scheme, bl_disk: str, chroot: str):
        self.scheme = scheme
        self.chroot = chroot
        self.bl_disk = bl_disk

        self.unmount_target_system(self.chroot)  # unmount all before start

    def mount_target_system(self, root):
        SpawnedSU.do(f"mkdir -p {root}")
        self.scheme.execute(Involve(chroot=root))

        SpawnedSU.do(f"""
            mount -t proc none {root}/proc
            for n in sys dev etc/resolv.conf; do
                mount --bind /$n {root}/$n;
            done
            """)

    def unmount_target_system(self, root):
        SpawnedSU.do(f"""
            for n in proc sys dev etc/resolv.conf; do
                umount {root}/$n;
            done
            """)

        self.scheme.execute(Release())

    @staticmethod
    def setup_bootloader(root, bl_disk):
        # grub-install --target=x86_64-efi --efi-directory={root}/boot/efi --boot-directory={root}/boot \
        # --uefi-secure-boot --bootloader-id=GRUB --recheck {bl_disk}

        Chroot.do(root, 'echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub')
        Chroot.do(root, 'yes 2>/dev/null | apt install grub-efi-amd64-signed grub-efi-amd64 && update-grub')

        # Set the kernel parameters, so that the initramfs can unlock the encrypted root partition.
        # Using the encrypt hook:
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX="... cryptdevice=UUID=device-UUID:cryptlvm ..."

    @staticmethod
    def setup_crypttab(root):
        Chroot.do(root, f"""
            echo "LUKS_BOOT UUID=$(blkid -s UUID -o value ${DEV}p1) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab
            echo "${DM}5_crypt UUID=$(blkid -s UUID -o value ${DEV}p5) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab
            """)

    @staticmethod
    def setup_fstab():
        pass

    @staticmethod
    def setup_resume():
        pass

    @staticmethod
    def setup_initramfs(root):
        Chroot.do(root, "update-initramfs -u -k all")

    def run(self):
        self.mount_target_system(self.chroot)

        self.setup_bootloader(self.chroot, self.bl_disk)
        # self.setup_crypttab()
        # self.setup_fstab()
        # self.setup_resume()
        self.setup_initramfs(self.chroot)
        #
        # self.unmount_target_system(self.chroot)

