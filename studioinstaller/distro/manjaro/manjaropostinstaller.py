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

from pathlib import Path

from spawned import ChrootContext

from ...partition import PVLuks
from ..postinstaller import PostInstaller
from ...partition.base import LUKS, Container
from ... import util

__all__ = ['ManjaroPostInstaller']


class ManjaroPostInstaller(PostInstaller):
    def _run(self):
        self.mounter.mount_target_system()

        with ChrootContext(self.op.chroot) as cntx:
            self.setup_bootloader(cntx)

            luks_volumes = self.scheme.partitions(LUKS, Container)
            self.setup_luks_volumes(cntx, luks_volumes)

        self.mounter.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mounter.mount_target_system()

        # install the tool into the target OS

        self.mounter.unmount_target_system()

    def setup_bootloader(self, cntx):
        grub_id = self.op.L

        # root partition
        partition_root = util.root_partition(self.scheme)
        partition_root_encrypted = any(isinstance(p, PVLuks) for p in partition_root.pchain)

        root_pv_uuid = ''
        while not root_pv_uuid:
            for pt in partition_root.pchain:
                if isinstance(pt, PVLuks):
                    root_pv_uuid = pt.uuid

        root_mapper_id = ''
        while not root_mapper_id:
            for pt in partition_root.pchain:
                if isinstance(pt.parent, PVLuks):
                    root_mapper_id = pt.mapperID

        cryptdevice_param = f"cryptdevice=UUID={root_pv_uuid}:{root_mapper_id}" if root_pv_uuid else ""
        cryptdevice_options = ":allow-discards" if cryptdevice_param and util.is_volume_on_ssd(partition_root) else ""

        grub_cmdline_linux = f"{cryptdevice_param}{cryptdevice_options}"

        config_root_encrypted = rf"""
            sed -Ei 's,GRUB_CMDLINE_LINUX="(.*)",GRUB_CMDLINE_LINUX="\1 {grub_cmdline_linux}",' /etc/default/grub
            """
        enable_root_encrypted = config_root_encrypted if partition_root_encrypted else ""

        # boot partition
        partition_boot = util.boot_partition(self.scheme)
        partition_boot_encrypted = any(isinstance(p, PVLuks) for p in partition_boot.pchain)

        config_grub_encrypted = rf"""
            FILE=/etc/default/grub

            grep "GRUB_ENABLE_CRYPTODISK=y" $FILE \
            && sed -i s/^#GRUB_ENABLE_CRYPTODISK=y/GRUB_ENABLE_CRYPTODISK=y/ $FILE \
            || echo "GRUB_ENABLE_CRYPTODISK=y" >> $FILE
            """
        enable_grub_encrypted = config_grub_encrypted if partition_boot_encrypted else ""

        # bootloader installation command
        if util.uefi_loaded():
            grub_install = f"grub-install --recheck --efi-directory=/boot/efi --bootloader-id={grub_id} --boot-directory=/boot"
        else:
            grub_install = f"grub-install --recheck --boot-directory=/boot {self.disk}"

        # execute installation
        cntx.do(f"""
            pacman --noconfirm -S grub
            {enable_root_encrypted}
            {enable_grub_encrypted}
            {grub_install}
            update-grub
            """)

    def setup_luks_volumes(self, cntx, volumes):
        # guard: keyfiles unnecessary
        if not volumes:
            return

        # guard: unencrypted /boot => don't use keyfiles !
        if not any(isinstance(p, PVLuks) for p in util.boot_partition(self.scheme).pchain):
            return

        keyfile = "/root/boot_os.keyfile"
        cryptkey_param = f"cryptkey=rootfs:{keyfile}"

        generate_keyfile(cntx, keyfile)

        for pt in volumes:
            luks_add_key(cntx, pt, keyfile)

            # skip adding a luks partition with the root FS inside; it's unlocked via a kernel parameter
            if any(pt == p for p in util.root_partition(self.scheme).pchain):
                continue

            opts = "luks"
            if util.disc_discardable(pt):
                opts += ",discard"
            cntx.do(f'echo "{pt.mapperID} UUID={pt.uuid} {keyfile} {opts}" >> /etc/crypttab')

        cntx.do(rf"""
            sed -Ei 's,FILES=\((.*)\),FILES=(\1 {keyfile}),' /etc/mkinitcpio.conf
            mkinitcpio -P
            chmod 600 /boot/initramfs-*

            sed -Ei 's,GRUB_CMDLINE_LINUX="(.*)",GRUB_CMDLINE_LINUX="\1 {cryptkey_param}",' /etc/default/grub
            update-grub
            """)


def generate_keyfile(cntx, keyfile):
    keyfile_dir = Path(keyfile).parent

    cntx.do(f"""
        mkdir -p {keyfile_dir}

        if [ -f {keyfile}.orig ]; then
            cp {keyfile}.orig {keyfile}
        else
            dd if=/dev/random of={keyfile} bs=512 count=4 iflag=fullblock
            chmod 600 {keyfile}
            cp {keyfile} {keyfile}.orig
        fi
        """)


def luks_add_key(cntx, pt, key):
    if util.test_luks_key(pt.url, '/'.join([cntx.root, key])):
        return

    with cntx.doi(f"cryptsetup luksAddKey {pt.url} {key}") as t:
        t.interact("Enter any existing passphrase:", pt.passphrase)
