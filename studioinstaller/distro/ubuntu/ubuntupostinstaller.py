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
#  Copyright (c) 2020 remico

"""Post-installation setup"""

from pathlib import Path

from spawned import ChrootContext, ENV, Spawned

from ..postinstaller import PostInstaller
from ...configfile import IniConfig, FstabConfig
from ...partition.base import LUKS, Container, FS
from ...runtimeconfig import RuntimeConfig
from ... import util

__all__ = ['UbuntuPostInstaller']


class UbuntuPostInstaller(PostInstaller):
    def _run(self):
        self.mounter.mount_target_system()

        with ChrootContext(self.op.chroot) as cntx:
            # TODO check if /boot is encrypted and pass cryptoboot accordingly
            setup_bootloader(cntx, self.disk, grub_id=self.op.L, cryptoboot=True)

            luks_volumes = self.scheme.partitions(LUKS, Container)
            setup_luks_volumes(cntx, luks_volumes)

            setup_fstab(cntx, self.scheme)
            # setup_resume(cntx)
            cntx.do("update-initramfs -u -k all")
            setup_fstrim_timer(cntx)

        self.mounter.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mounter.mount_target_system()

        with ChrootContext(self.op.chroot) as cntx:
            cntx.do("apt -q install -y python3-pip git > /dev/null")

            # install the tool into the target system
            x_all = '[seed]' if extras else ''
            x_extras = '--pre' if develop else ''
            cmd_inject = f"pip3 install -U --force-reinstall --extra-index-url=https://remico.github.io/pypi " \
                         f"studioinstaller{x_all} {x_extras}"

            with cntx.doi(cmd_inject) as t:
                t.interact_user()

        self.mounter.unmount_target_system()


def setup_bootloader(cntx, grub_disk, grub_id=None, cryptoboot=False):
    cmd_is_cryptoboot_enabled = 'grep "GRUB_ENABLE_CRYPTODISK=y" /etc/default/grub'
    cmd_enable_cryptoboot = 'echo "GRUB_ENABLE_CRYPTODISK=y" >> /etc/default/grub' if cryptoboot else 'true'

    if util.system.uefi_loaded():
        deps = "apt -q install -y grub-efi > /dev/null"
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


def setup_luks_volumes(cntx, volumes):
    if volumes:
        keyfile = "/etc/luks/boot_os.keyfile"
        cntx.do("apt -q install -y cryptsetup-initramfs > /dev/null")
        create_keys(cntx, keyfile)

    cntx.do(f"truncate -s 0 /etc/crypttab")  # fill /etc/crypttab from scratch
    for pt in volumes:
        luks_add_key(cntx, pt.url, keyfile, pt.passphrase)

        opts = "luks"
        if util.blockdevice.discardable(pt):
            opts += ",discard"
        cntx.do(f'echo "{pt.mapperID} UUID={pt.uuid} {keyfile} {opts}" >> /etc/crypttab')


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


def luks_add_key(cntx, pt_url, key, passphrase):
    if util.blockdevice.test_luks_key(pt_url, '/'.join([cntx.root, key])):
        return

    with cntx.doi(f"cryptsetup luksAddKey {pt_url} {key}") as t:
        t.interact("Enter any existing passphrase:", passphrase)


def setup_fstab(cntx, scheme):
    fstab = FstabConfig(cntx)

    for pt in scheme.partitions(FS):
        can_auto_mount = bool(pt.mountpoint and pt.fs)
        if can_auto_mount and not fstab.contains(pt):
            volume = f"UUID={pt.uuid}" if pt.isphysical else pt.url
            opts = "defaults,relatime"
            fstab.append(volume, pt.mountpoint, pt.fs, opts)

        # assume that additional user partitions are mounted in /media
        if "/media" in pt.mountpoint:
            user = util.target.target_user(cntx.root)
            cntx.do(f"chown -R {user}:{user} {pt.mountpoint}")


def setup_resume(cntx):
    pass


def setup_fstrim_timer(cntx):
    tc = IniConfig("/lib/systemd/system/fstrim.timer", cntx)
    tc.replace(r"OnCalendar=.*", "OnCalendar=daily")
