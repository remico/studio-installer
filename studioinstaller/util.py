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

from spawned import SpawnedSU, Spawned, logger, create_py_script

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
           'data_file',
           'preseeding_file',
           'is_trim_supported',
           'tagged_printer',
           'cmd_edit_inplace',
           ]


def is_efi_boot():
    efi_vars = Spawned.do("mount | grep efivars")
    return bool(efi_vars)


def is_volume_on_ssd(volume_url):
    return not int(Spawned.do(f"lsblk -n -d -o ROTA {volume_url}").strip())


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
    return bool(SpawnedSU.do(f"cryptsetup open --test-passphrase -d {key} {volume_url} && echo True"))


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


def data_file(filename):
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


def tagged_printer(tag: str):
    @logger.tagged(tag, logger.ok_blue_s)
    def _p(*text: str):
        return text
    return _p


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
