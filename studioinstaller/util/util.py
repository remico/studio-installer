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

"""Useful functions"""

import os
import stat
from pathlib import Path
from time import sleep

from spawned import SpawnedSU, Spawned, logger, create_py_script, ask_user, ENV, SETENV

__all__ = ['uefi_loaded',
           'is_volume_on_ssd',
           'volume_uuid',
           'test_luks_key',
           'resource_file',
           'preseeding_file',
           'disc_discardable',
           'tagged_printer',
           'cmd_edit_inplace',
           'target_user',
           'target_home',
           'deploy_resource',
           'os_stat',
           'is_readable',
           'is_editable',
           'owner_uid',
           'ready_for_postinstall',
           'get_target_upass',
           'read_upass_from_preseeding_file',
           'distro_name',
           'boot_partition',
           'root_partition',
           'delay',
           ]


# TODO lsblk -o name,type,path,mountpoint,rota,uuid,disc-gran,disc-max,label,partlabel --json /dev/sd*
# -l -n

def tagged_printer(tag: str):
    @logger.tagged(tag, logger.ok_blue_s)
    def _p(*text: str):
        return text
    return _p


_tp = tagged_printer("[util]")


def uefi_loaded():
    return Spawned.do("mount | grep efivars", with_status=True).success


def is_volume_on_ssd(volume_url):
    return Spawned.do(f"lsblk -n -d -o ROTA {volume_url}").strip() == "0"  # 0 - SSD, 1 - HDD


def disc_discardable(partition):
    pattern = "TRIM supported"
    return is_volume_on_ssd(partition.url) and \
        pattern in SpawnedSU.do(f'sudo hdparm -I {partition.disk} | grep "{pattern}"')


def volume_uuid(volume_url):
    return SpawnedSU.do(f"blkid -s UUID -o value {volume_url}")


def test_luks_key(volume_url, key):
    return SpawnedSU.do(
            f"cryptsetup open --test-passphrase -d {key} {volume_url} 2>/dev/null",
            with_status=True
        ).success


def resource_file(filename):
    """Returns the first available file with matching name"""
    from importlib.metadata import files as app_files
    if l := [f for f in app_files(__package__) if str(f).endswith(filename)]:
        return str(l[0].locate())
    return ""


def preseeding_file():
    """Returns the first available .seed file"""
    # TODO move .seed file inside the package and use resource API
    from importlib.metadata import files as app_files
    if l := [f for f in app_files(__package__) if str(f).endswith('.seed')]:
        return str(l[0].locate())
    return ""


_edit_inplace_script = create_py_script(r"""
import fileinput
import re, sys

_a = sys.argv
filepath = _a[1]
re_pattern = _a[2]
replacement = _a[3]

with fileinput.FileInput(filepath, inplace=True) as f:
    for line in f:
        print(re.sub(re_pattern, replacement, line), end='')
""")


def cmd_edit_inplace(filepath: str, re_old: str, str_new: str):
    return f'python3 "{_edit_inplace_script}" "{filepath}" "{re_old}" "{str_new}"'


def target_user(root_fs: str):
    return Spawned.do(f'ls {root_fs}/home/ | grep -v "lost+found"')


def target_home(root_fs: str):
    return f"{root_fs}/home/{user}" if (user := target_user(root_fs)) else ""


def deploy_resource(filename, dst_path, owner=None, mode=None):
    src_path = resource_file(filename)
    dst_full_path = dst_path if dst_path.endswith(filename) else f"{dst_path}/{filename}"

    if not Path(dst_full_path).parent.exists():
        colored_warn = logger.fail_s("WARNING:")
        _tp(f"{colored_warn} Path {Path(dst_full_path).parent} doesn't exist; deploy_resource('{filename}') skipped")
        return  # just skip processing for now

    owner = owner or owner_uid(Path(dst_full_path).parent)
    mode = mode or 0o664

    SpawnedSU.do(f"cp {src_path} {dst_path}")
    SpawnedSU.do(f"chown {owner}:{owner} {dst_full_path}")
    SpawnedSU.do(f"chmod {mode} {dst_full_path}")


def os_stat(path: str):
    return os.stat(path)


def is_readable(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return bool(statinfo_or_path.st_mode & (stat.S_IRUSR | stat.S_IRGRP))


def is_editable(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return bool(statinfo_or_path.st_mode & (stat.S_IWUSR | stat.S_IWGRP))


def owner_uid(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return statinfo_or_path.st_uid


def ready_for_postinstall(chroot):
    """True if the chroot path exists and nothing mounted inside, False otherwise"""
    path = Path(chroot)
    return path.exists() and not any(path.iterdir())


def get_target_upass(insystem_scheduled):
    if tupass := ENV('TUPASS'):
        return tupass

    tupass = read_upass_from_preseeding_file("user-password")

    if not tupass and not insystem_scheduled:
        tupass = read_upass_from_preseeding_file("user-password-crypted")

    if not tupass:
        tupass = ask_user("Enter user password for target system:")

    SETENV('TUPASS', tupass)
    return tupass


def read_upass_from_preseeding_file(pass_key):
    prefile = preseeding_file()
    if not prefile:
        return ""

    template = f"grep 'passwd/%s' {prefile} | grep -vP '#' | cut -d' ' -f4"
    return Spawned.do(template % pass_key)


def distro_name():
    return Spawned.do("less /etc/lsb-release | grep -oP '(?<=DISTRIB_ID=).*'")


def boot_partition(scheme):
    for pt in scheme:
        if pt.mountpoint == "/boot":
            return pt

    return root_partition(scheme)


def root_partition(scheme):
    for pt in scheme:
        if pt.mountpoint == "/":
            return pt


def delay(sec):
    print()
    for i in range(sec):
        print('.', end='')
        sleep(1)
    print()
