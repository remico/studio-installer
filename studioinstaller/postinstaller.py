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

""" Post-installation setup """

from .partition.base import Partition
from .partitioner import Partitioner
from .scheme import Scheme
from .spawned import SpawnedSU, logger as log

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PostInstaller']


class PostInstaller:
    def __init__(self, scheme: Scheme):
        self.scheme = scheme

    def mount_target_system(self):
        # SpawnedSU.do_script(f"""
        #     swapon /dev/{vg_name}/swap
        #     mount /dev/{vg_name}/root /mnt
        #     mount /dev/{vg_name}/home /mnt/home
        #     mount {partition_efi} /mnt/boot/efi
        #     """)
        root = self.scheme.partition('/')
        home = self.scheme.partition('/home')
        SpawnedSU.do_script(f"""
            mount {root} /target
            mount {home} /target/home 
            for n in proc sys dev etc/resolv.conf; do
                mount --rbind /$n /target/$n;
            done
            chroot /target
            mount -a
            """)


    def umount_target_system(self):
        pass

    def handle_mountpoints(self):
        pass
        # if a mountpoint specified in the partitioning scheme, but the path doesn't exist => create it in the FS
        # and register in fstab (and crypttab)

    def setup_fstab(self):
        pass

    def setup_crypttab(self, target_root):
        SpawnedSU.do_script(f"""
            echo "LUKS_BOOT UUID=$(blkid -s UUID -o value ${DEV}p1) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab
            echo "${DM}5_crypt UUID=$(blkid -s UUID -o value ${DEV}p5) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab
            """)

    def setup_initramfs(self):
        # mount all partitions ?
        # configure RESUME
        # configure /etc/crypttab
        # configure /etc/fstab (root, boot, swap)
        #
        SpawnedSU.do("sudo update-initramfs -u -k all")

    def setup_bootloader(self, disk):
        SpawnedSU.do('echo "GRUB_ENABLE_CRYPTODISK=y" >> /target/etc/default/grub')

        ## Set the kernel parameters, so that the initramfs can unlock the encrypted root partition. Using the encrypt hook:
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX="... cryptdevice=UUID=device-UUID:cryptlvm ..."

        ## install GRUB
        # grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB --recheck

        ## Generate GRUB's configuration file:
        # grub-mkconfig -o /boot/grub/grub.cfg
        # update-grub2
