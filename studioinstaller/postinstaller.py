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

from pathlib import Path

from spawned import SpawnedSU, Chroot, ChrootContext

from .action import Involve, Release
from .partition.base import LUKS, Container
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

    def run(self):
        self.mount_target_system()

        with ChrootContext(self.chroot) as cntx:
            reset_changes(cntx)

            setup_bootloader(cntx, self.bl_disk, "studio")

            keyfile = "/etc/luks/boot_os.keyfile"

            cntx.do("apt install -y cryptsetup-initramfs")
            create_keys(cntx, keyfile)

            for pt in self.scheme.partitions(LUKS, Container):
                luks_add_key(cntx, pt.url, keyfile, pt.passphrase)
                cntx.do(f'echo "{pt.mapperID} UUID={pt.uuid} {keyfile} luks,discard" >> /etc/crypttab')

            # setup_fstab(cntx)
            # setup_resume(cntx)

            cntx.do("update-initramfs -u -k all")

        self.unmount_target_system()


def setup_bootloader(cntx, grub_disk, grub_id=None):
    grub_id_opt = f"--no-uefi-secure-boot --bootloader-id={grub_id}" if grub_id else ""

    cntx.do(f"""
        echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub
        apt install -y grub-efi

        grub-install --target=x86_64-efi --efi-directory=/boot/efi \
            --boot-directory=/boot --recheck {grub_id_opt} {grub_disk}

        update-grub
        """)


def create_keys(cntx, keyfile):
    keyfile_dir = Path(keyfile).parent
    cntx.do(f"""
        echo "KEYFILE_PATTERN={keyfile_dir}/*.keyfile" >> /etc/cryptsetup-initramfs/conf-hook
        echo "UMASK=0077" >> /etc/initramfs-tools/initramfs.conf

        mkdir -p {keyfile_dir}

        if [ -f {keyfile}.orig ]; then
            cp {keyfile}.orig {keyfile}
        else
            dd if=/dev/urandom of={keyfile} bs=4096 count=1
            cp {keyfile} {keyfile}.orig
        fi

        chmod u=rx,go-rwx {keyfile_dir}
        chmod u=r,go-rwx {keyfile}
        """)


# TODO think of:
#  - add new Action LuksAddKey and PostInstall actions
#  - or add parameter to Encrypt(addKey={device: key|keyfile, all: key|keyfile})
def luks_add_key(cntx, pt_url, key, passphrase):
    with cntx.doi(f"cryptsetup luksAddKey {pt_url} {key}") as t:
        t.interact("Enter any existing passphrase:", passphrase)


def setup_fstab(cntx):
    pass


def setup_resume(cntx):
    pass


def reset_changes(cntx):
    cntx.do(f"""
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

        rm -rf /boot/efi/*

        # apt remove -y grub-efi-amd64-bin
        # apt autoremove -y
        """)
