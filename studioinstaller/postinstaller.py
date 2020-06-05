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

from spawned import SpawnedSU, Chroot, ChrootContext

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
            for n in proc sys dev etc/resolv.conf; do
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

    def run(self):
        self.mount_target_system(self.chroot)

        reset_changes(self.chroot)

        setup_bootloader(self.chroot, self.bl_disk)

        keyfile = "boot_os.keyfile"
        create_keys(self.chroot, keyfile)
        # add_keys(self.chroot, keyfile)
        # setup_crypttab(self.chroot, keyfile)

        # setup_fstab(self.chroot)
        # setup_resume(self.chroot)
        setup_initramfs(self.chroot)
        #
        # self.unmount_target_system(self.chroot)


def setup_bootloader(root, bl_disk):
    Chroot(root).do(f"""
        echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub

        apt install -y grub-efi \
        && grub-install --target=x86_64-efi --efi-directory=/boot/efi \
            --boot-directory=/boot --uefi-secure-boot --bootloader-id=GRUB --recheck {bl_disk} \
        && update-grub
        """)

    # Set the kernel parameters, so that the initramfs can unlock the encrypted root partition.
    # Using the encrypt hook:
    # /etc/default/grub
    # GRUB_CMDLINE_LINUX="... cryptdevice=UUID=device-UUID:cryptlvm ..."


def create_keys(root, keyfile):
    Chroot(root).do(f"""
        echo "KEYFILE_PATTERN=/etc/luks/*.keyfile" >> /etc/cryptsetup-initramfs/conf-hook
        echo "UMASK=0077" >> /etc/initramfs-tools/initramfs.conf

        mkdir -p /etc/luks

        if [ -f /etc/luks/{keyfile}.orig ]; then
            cp /etc/luks/{keyfile}.orig /etc/luks/{keyfile}
        else
            dd if=/dev/urandom of=/etc/luks/{keyfile} bs=4096 count=1
            cp /etc/luks/{keyfile} /etc/luks/{keyfile}.orig
        fi

        chmod u=rx,go-rwx /etc/luks
        chmod u=r,go-rwx /etc/luks/{keyfile}
        """)


# TODO add new Action LuksAddKey and PostInstall actions
# TODO or add parameter to Encrypt(addKey={device: key|keyfile, all: key|keyfile})
def luks_add_key(luks_device, key, passphrase):
    for pt in scheme.partitions(LUKS, PV, Container):
        with SpawnedSU(f"cryptsetup luksAddKey {luks_device} {key}") as t:
            t.interact("Enter any existing passphrase:", passphrase)


def setup_crypttab(root, keyfile):
    Chroot(root).do(f"""
        apt install -y cryptsetup-initramfs

        # echo "LUKS_BOOT UUID=$(blkid -s UUID -o value ${DEV}p1) /etc/luks/{keyfile} luks,discard" >> /etc/crypttab
        # echo "${DM}5_crypt UUID=$(blkid -s UUID -o value ${DEV}p5) /etc/luks/{keyfile} luks,discard" >> /etc/crypttab
        """)


def setup_fstab():
    pass


def setup_resume():
    pass


def setup_initramfs(root):
    Chroot(root).do("update-initramfs -u -k all")


def reset_changes(root):
    Chroot(root).do(f"""
        if [ ! -f /etc/default/grub.orig ]; then cp /etc/default/grub /etc/default/grub.orig; fi
        if [ ! -f /etc/fstab.orig ]; then cp /etc/fstab /etc/fstab.orig; fi
        if [ ! -f /etc/cryptsetup-initramfs/conf-hook.orig ]; then
            cp /etc/cryptsetup-initramfs/conf-hook /etc/cryptsetup-initramfs/conf-hook.orig
        fi
        if [ ! -f /etc/initramfs-tools/initramfs.conf.orig ]; then
            cp /etc/initramfs-tools/initramfs.conf /etc/initramfs-tools/initramfs.conf.orig
        fi

        cp /etc/default/grub.orig /etc/default/grub
        cp /etc/fstab.orig /etc/fstab
        cp /etc/cryptsetup-initramfs/conf-hook.orig /etc/cryptsetup-initramfs/conf-hook
        cp /etc/initramfs-tools/initramfs.conf.orig /etc/initramfs-tools/initramfs.conf
        truncate -s 0 /etc/crypttab
        """)
