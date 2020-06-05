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

"""Manipulates partman's file markers according to the partman rules

   partman's rules can't handle existing partitions in automatic mode clearly, but in manual mode - it can.
   so the main idea is in emulating of "manual" user actions by tracking the partman's DB in background
   and manipulate the special marker files inside, according to predefined partitioning requirements
"""

import re
from pathlib import Path

from spawned import SpawnedSU, Spawned, create_py_script

from .scheme import Scheme

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PartmanCheater']


class PathResolver:
    PARTMAN_BASE = Path("/var/lib/partman")

    def __init__(self):
        self._system_volumes = {}

    @staticmethod
    def _pm_encode(device_path: str):
        return device_path.replace("/", "=")

    @staticmethod
    def _pm_path(disk: str):
        return Path(PathResolver.PARTMAN_BASE, 'devices', PathResolver._pm_encode(disk))

    @property
    def system_volumes(self):
        if not self._system_volumes:
            t = SpawnedSU("parted /dev/sda 'unit B print all'")  # hardcoded /dev/sda does not affect result

            current_key = ""

            disk_name_pat = r"Disk[\s\t]+(.*?):[\s\t]+\d+"
            partition_number_pat = r"(\d+)[\s\t]+(\d+)B[\s\t]+(\d+)B[\s\t]+(\d+)B"

            def prsr(data_line):
                nonlocal current_key

                if mo := re.search(disk_name_pat, data_line):
                    # group-1 : disk, e.g. /dev/sda or /dev/mapper/swap
                    current_key = mo.group(1)
                    return
                elif mo := re.search(partition_number_pat, data_line):
                    # group-1 : partition number (1, 2, 3, ...)
                    # group-2 : first Byte of the partition
                    # group-3 : last Byte of the partition
                    volume_key = current_key if "mapper" in current_key else current_key + mo.group(1)
                    # return a tuple ('volume', 'begin-end', 'disk') for each partition
                    return volume_key, "-".join((mo.group(2), mo.group(3))), current_key

            self._system_volumes = {tpl[0]: (tpl[1], tpl[2]) for line in t.datalines if (tpl := prsr(line))}

        return self._system_volumes

    def system_disk(self, volume: str):
        return self.system_volumes[volume][1]

    def pm_volume_name(self, volume: str):
        return self.system_volumes[volume][0]

    def pm_resolve_device(self, volume: str):
        return self._pm_path(self.system_volumes[volume][1])

    def pm_resolve_volume(self, volume: str):
        return self.pm_resolve_device(volume).joinpath(self.pm_volume_name(volume))


def _text_replacer():
    re_pattern = r"\${!TAB}\${!TAB}\${!TAB}(\w+)\${!TAB}\${!TAB}\${!TAB}"
    re_replacement = r"${!TAB}${!TAB}%s${!TAB}\1${!TAB}${!TAB}%s${!TAB}"

    script = f"""
import sys, re, fileinput

file = sys.argv[1]
format = True if sys.argv[2] == "True" else False
mountpoint = sys.argv[3]

pattern = {re_pattern}
repl = {re_replacement} % ('F' if format else 'K', mountpoint)

try:
    with fileinput.FileInput(file, inplace=True, backup='.bak') as f:
        for line in f:
            print(re.sub(pattern, repl, line), end='')
except FileNotFoundError:
    pass
    """
    return script


class PartmanCheater:
    visuals_updater = create_py_script(_text_replacer())

    def __init__(self, scheme: Scheme):
        self.scheme = scheme
        self.resolver = PathResolver()

    def run(self):
        SpawnedSU.do_script(f"""
            echo "Waiting for PARTMAN files in '{PathResolver.PARTMAN_BASE}' ..."
            while [ ! -d {PathResolver.PARTMAN_BASE} ]; do
                sleep 1
            done
            echo ""PARTMAN files found. Ready for processing.""
            """)

        for p in self.scheme:
            if p.mountpoint and not p.isspecial:
                self.mark_to_use(p.url, p.mountpoint, p.do_format, p.fs)

    # do not use: filesystem {<last_manually_specified>}, existing, formatable
    # use as is: ++ acting_filesystem {ext4}, method {keep}, use_filesystem
    # format: ++ method {format}, format
    # use mounted: ++ mountpoint {<path>}
    def mark_to_use(self, volume, mountpoint, format, fs):
        volume_path = self.resolver.pm_resolve_volume(volume)
        SpawnedSU.do_script(f"""
            while [ ! -d {volume_path} ]
            do
                sleep 1
                echo "waiting for {volume_path} ..."
            done

            partman_volume={volume_path}

            touch ${{partman_volume}}/existing
            touch ${{partman_volume}}/formatable
            touch ${{partman_volume}}/use_filesystem
            echo "{mountpoint}" > ${{partman_volume}}/mountpoint

            if [ "{format}" == "True" ]; then
                touch ${{partman_volume}}/format
                echo "format" > ${{partman_volume}}/method
                echo "{fs}" > ${{partman_volume}}/filesystem
                echo "{fs}" > ${{partman_volume}}/acting_filesystem
            else
                echo "keep" > ${{partman_volume}}/method
                
                while [ ! -f ${{partman_volume}}/detected_filesystem ]
                do
                    sleep 1
                    echo "waiting for ${{partman_volume}}/detected_filesystem ..."
                done

                cat ${{partman_volume}}/detected_filesystem > ${{partman_volume}}/acting_filesystem
                cat ${{partman_volume}}/detected_filesystem > ${{partman_volume}}/filesystem
            fi

            # replace visuals
            echo "{mountpoint}" > ${{partman_volume}}/visual_mountpoint
            python3 {self.visuals_updater} ${{partman_volume}}/view "{format}" "{mountpoint}"
            python3 {self.visuals_updater} ${{partman_volume}}/../partition_tree_cache "{format}" "{mountpoint}"
            python3 {self.visuals_updater} {PathResolver.PARTMAN_BASE}/snoop "{format}" "{mountpoint}"
            """)
