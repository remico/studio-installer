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

from spawned import SpawnedSU, ChrootContext

from .action import Involve, Release
from .configfile import IniConfig, FstabConfig
from .partition.base import LUKS, Container, FS
from .scheme import Scheme
from . import util

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

    def run(self, extra=False):
        self.mount_target_system()

        with ChrootContext(self.chroot) as cntx:
            self._run_mandatory(cntx)
            if extra:
                self._run_extra(cntx)

        self.unmount_target_system()

    def _run_mandatory(self, cntx):
        # TODO check if /boot is encrypted and pass cryptoboot accordingly
        setup_bootloader(cntx, self.bl_disk, grub_id="studio", cryptoboot=True)

        luks_volumes = self.scheme.partitions(LUKS, Container)

        if luks_volumes:
            keyfile = "/etc/luks/boot_os.keyfile"
            cntx.do("apt install -y cryptsetup-initramfs")
            create_keys(cntx, keyfile)

        cntx.do(f"truncate -s 0 /etc/crypttab")  # fill /etc/crypttab from scratch
        for pt in luks_volumes:
            luks_add_key(cntx, pt.url, keyfile, pt.passphrase)

            opts = "luks"
            if util.is_trim_supported(pt):
                opts += ",discard"
            cntx.do(f'echo "{pt.mapperID} UUID={pt.uuid} {keyfile} {opts}" >> /etc/crypttab')

        setup_fstab(cntx, self.scheme)
        # setup_resume(cntx)

        cntx.do("update-initramfs -u -k all")

        # adjust fstrim timer
        tc = IniConfig("/lib/systemd/system/fstrim.timer", cntx)
        tc.replace(r"OnCalendar=.*", "OnCalendar=daily")

    def _run_extra(self, cntx):
        install_software(cntx)


def setup_bootloader(cntx, grub_disk, grub_id=None, cryptoboot=False):
    cmd_is_cryptoboot_enabled = 'grep "GRUB_ENABLE_CRYPTODISK=y" /etc/default/grub'
    cmd_enable_cryptoboot = 'echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub' if cryptoboot else 'true'

    if util.is_efi_boot():
        deps = "apt install -y grub-efi"
        opts = "--target=x86_64-efi"
        grub_id_opt = f"--no-uefi-secure-boot --bootloader-id={grub_id}" if grub_id else ""
    else:
        deps = ""
        opts = ""
        grub_id_opt = ""

    cntx.do(f"""
        {cmd_is_cryptoboot_enabled} || {cmd_enable_cryptoboot}
        {deps}
        grub-install --recheck {opts} {grub_id_opt} {grub_disk}
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
    if util.test_luks_key(pt_url, '/'.join([cntx.root, key])):
        return

    with cntx.doi(f"cryptsetup luksAddKey {pt_url} {key}") as t:
        t.interact("Enter any existing passphrase:", passphrase)


def setup_fstab(cntx, scheme):
    fstab = FstabConfig(cntx)

    for pt in scheme.partitions(FS):
        can_auto_mount = bool(pt.mountpoint and pt.fs)
        if can_auto_mount and not util.is_in_fstab(pt, fstab.abs_filepath):
            volume = f"UUID={pt.uuid}" if pt.isphysical else pt.url
            opts = "defaults,noatime"
            fstab.append(volume, pt.mountpoint, pt.fs, opts)


def setup_resume(cntx):
    pass


def install_software(cntx):
    pass
