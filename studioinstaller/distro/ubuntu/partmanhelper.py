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

"""Manipulates partman's file markers according to the partman rules

   partman's rules can't handle existing partitions in automatic mode clearly, but in manual mode - it can.
   so the main idea is in emulating of "manual" user actions by tracking the partman's DB in background
   and manipulate the special marker files inside, according to predefined partitioning requirements
"""

import re
from pathlib import Path

from spawned import Spawned, SpawnedSU, create_py_script

from ...scheme import Scheme
from ...util import tagged_logger

__all__ = ['PartmanHelper']


_tlog = tagged_logger("[PartmanHelper]")

PARTMAN_BASE = Path("/var/lib/partman")


class PathResolver:
    def __init__(self):
        self._system_volumes = {}

    @property
    def system_volumes(self):
        if not self._system_volumes:
            t = SpawnedSU("parted -s /dev 'unit B print all' 2>/dev/null")

            current_key = ""

            re_disk_name = r"Disk[\s\t]+(.*?):[\s\t]+\d+"
            re_partition_number = r"(\d+)[\s\t]+(\d+)B[\s\t]+(\d+)B[\s\t]+(\d+)B"

            def geometry_parser(data_line):
                nonlocal current_key

                if mo := re.search(re_disk_name, data_line):
                    # group-1 : disk, e.g. /dev/sda or /dev/mapper/swap
                    current_key = mo.group(1)
                    return
                elif mo := re.search(re_partition_number, data_line):
                    partition_number = mo.group(1)
                    first_byte = mo.group(2)
                    last_byte = mo.group(3)
                    volume_key = current_key if "mapper" in current_key else current_key + partition_number
                    # returns a tuple ('volume_url', 'begin-end', 'disk_url') for each partition
                    return volume_key, f"{first_byte}-{last_byte}", current_key

            # {volume_url: (begin-end, disk_url)}
            self._system_volumes = {tpl[0]: (tpl[1], tpl[2]) for line in t.datalines if (tpl := geometry_parser(line))}

        return self._system_volumes

    def volume(self, volume_url: str):
        try:
            return self.system_volumes[volume_url]
        except KeyError:  # fallback: try LVM LV name conversion rules
            _v = volume_url.split('/')
            if len(_v) == 4:
                volume_url = f"/dev/mapper/{_v[2].replace('-', '--')}-{_v[3]}"
                return self.system_volumes[volume_url]
            raise

    def system_disk(self, volume_url: str):
        return self.volume(volume_url)[1]  # disk_url

    def pm_resolve_volume_name(self, volume_url: str):
        return self.volume(volume_url)[0]  # volume's begin-end, partman uses it as the volume name

    def pm_resolve_disk_path(self, volume_url: str):
        # partman uses '=' instead of '/' in paths
        disk = self.system_disk(volume_url)
        return Path(PARTMAN_BASE, 'devices', disk.replace("/", "="))

    def pm_resolve_volume_path(self, volume_url: str):
        pm_volume_name = self.pm_resolve_volume_name(volume_url)
        pm_disk = self.pm_resolve_disk_path(volume_url)
        return Path(pm_disk, pm_volume_name)


def re_script():
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


class PartmanHelper:

    def __init__(self, scheme: Scheme):
        self.scheme = scheme
        self.resolver = PathResolver()

    def run(self):
        # check partman availability
        if not Spawned.do("which partman", with_status=True).success:
            _tlog("[II] partman not found => skip PartmanHelper actions")
            return

        script = re_script()
        self.visuals_updater = create_py_script(script)

        SpawnedSU.do_script(f"""
            echo "Waiting for PARTMAN files in '{PARTMAN_BASE}' ..."
            while [ ! -d {PARTMAN_BASE} ]; do
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
    def mark_to_use(self, volume_url, mountpoint, do_format, fs):
        volume_path = self.resolver.pm_resolve_volume_path(volume_url)
        SpawnedSU.do_script(f"""
            while [ ! -d {volume_path} ]
            do
                sleep 1
                echo "waiting for {volume_path} ..."
            done

            touch {volume_path}/existing
            touch {volume_path}/formatable
            touch {volume_path}/use_filesystem
            echo "{mountpoint}" > {volume_path}/mountpoint

            if [ "{do_format}" == "True" ]; then
                touch {volume_path}/format
                echo "format" > {volume_path}/method
                echo "{fs}" > {volume_path}/filesystem
                echo "{fs}" > {volume_path}/acting_filesystem
            else
                echo "keep" > {volume_path}/method

                while [ ! -f {volume_path}/detected_filesystem ]
                do
                    sleep 1
                    echo "waiting for {volume_path}/detected_filesystem ..."
                done

                cat {volume_path}/detected_filesystem > {volume_path}/acting_filesystem
                cat {volume_path}/detected_filesystem > {volume_path}/filesystem
            fi

            # replace visuals
            echo "{mountpoint}" > {volume_path}/visual_mountpoint
            python3 "{self.visuals_updater}" "{volume_path}/view" "{do_format}" "{mountpoint}"
            python3 "{self.visuals_updater}" "{volume_path}/../partition_tree_cache" "{do_format}" "{mountpoint}"
            python3 "{self.visuals_updater}" "{PARTMAN_BASE}/snoop" "{do_format}" "{mountpoint}"
            """)
