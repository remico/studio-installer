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

"""Useful functions"""

import os
import stat
from pathlib import Path

from spawned import SpawnedSU, Spawned, logger, create_py_script, ask_user, ENV, SETENV

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['is_efi_boot',
           'is_volume_on_ssd',
           'volume_uuid',
           'is_in_fstab',
           'test_luks_key',
           'clear_installation_cache',
           'resource_file',
           'preseeding_file',
           'is_trim_supported',
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
           ]


def tagged_printer(tag: str):
    @logger.tagged(tag, logger.ok_blue_s)
    def _p(*text: str):
        return text
    return _p


_tp = tagged_printer("[util]")


def is_efi_boot():
    exit_status = Spawned.do("mount | grep efivars", with_status=True)
    return exit_status[0] == 0


def is_volume_on_ssd(volume_url):
    return Spawned.do(f"lsblk -n -d -o ROTA {volume_url}").strip() == "0"  # 0 - SSD, 1 - HDD


def is_trim_supported(partition):
    pattern = "TRIM supported"
    return is_volume_on_ssd(partition.url) and \
        pattern in SpawnedSU.do(f'sudo hdparm -I {partition.disk} | grep "{pattern}"')


def volume_uuid(volume_url):
    return SpawnedSU.do(f"blkid -s UUID -o value {volume_url}")


def is_in_fstab(partition, fstab_path):
    lvm_lv_vid = f"/dev/mapper/{partition.lvm_vg.replace('-', '--')}-{partition.lvm_lv}"
    return bool(Spawned.do(f"egrep '{partition.url}|{partition.uuid}|{lvm_lv_vid}' {fstab_path}"))


def test_luks_key(volume_url, key):
    exit_status = SpawnedSU.do(f"cryptsetup open --test-passphrase -d {key} {volume_url} 2>/dev/null", with_status=True)
    return exit_status[0] == 0


def clear_installation_cache():
    # clear partman cache
    SpawnedSU.do("rm -rf /var/lib/partman")

    # clear debconf cache
    # note: removing the DB leads the ubiquity installer to crash
    SpawnedSU.do_script("""
        if [ ! -d /var/cache/debconf.back ]; then
            cp -r /var/cache/debconf/ /var/cache/debconf.back
        else
            rm -rf /var/cache/debconf
            cp -r /var/cache/debconf.back /var/cache/debconf
        fi
        """)


def resource_file(filename):
    """Returns the first available file with matching name"""
    from importlib.metadata import files as app_files
    if l := [f for f in app_files(__package__) if str(f).endswith(filename)]:
        return l[0].locate()


def preseeding_file():
    """Returns the first available .seed file"""
    # TODO move .seed file inside the package and use resource API
    from importlib.metadata import files as app_files
    if l := [f for f in app_files(__package__) if str(f).endswith('.seed')]:
        return l[0].locate()


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
