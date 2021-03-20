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

"""Prepare partitions for OS installation according to the partitioning scheme"""

import re

from spawned import ask_user, logger as log, SpawnedSU

from .action import Create, Format
from .partition.base import Partition, FS
from .partition import LVLvm
from .scheme import Scheme
from .util import uefi_loaded

__all__ = ['PreInstaller']


class PreInstaller:
    def __init__(self, scheme: Scheme, op):
        self.scheme = scheme
        self.lukspass = ''
        self.op = op

        for pt in self.scheme:
            log.print_dict(pt)
            print("")

        self.validate_scheme()

    @property
    def passphrase(self):
        return self.lukspass or ask_user("Enter default LUKS passphrase:")

    def validate_scheme(self):
        assert self.scheme, "No partitioning scheme is defined"
        assert len(self.scheme.disks()) == 1, "All partitions in the scheme must belong to a single disk drive"

        for pt in self.scheme:
            assert isinstance(pt, Partition), "Partitioning scheme must contain Partition's only"
            assert pt.id, "Partition `id` can't be empty"
            assert pt.is_new, "All partitions in the scheme must be marked as New"
            assert pt.parent, f"No parent specified for {pt.id}"
            assert not pt.islvmlv or pt.lvm_vg, "No LVM VG is defined for an LVM LV"
            assert not pt.islvmlv or pt.lvm_vg in LVLvm.groups(self.scheme), "LVM VGs do not match"
            assert not pt.do_format or isinstance(pt, FS), f"Partition {pt.id} can't be formatted"
            assert "efi" not in pt.mountpoint or uefi_loaded(), \
                "Partitioning scheme contains a EFI partition while the system doesn't look to booted in EFI mode"

    def free_space_on_disks(self):
        for disk in self.scheme.disks():
            # ask for clearing the whole disk
            if 'y' == ask_user(f"Delete all partitions on disk '{disk.url}'? [y/N]:").lower():
                disk.create_new_partition_table()

            # otherwise ask for removing individual partitions
            else:
                t = SpawnedSU(f"parted {disk.url} print")
                partitions = [line.strip() for line in t.datalines if line.strip() and line.strip()[0].isdigit()]

                for partition in partitions:
                    print(f"Partition [[ {log.ok_blue_s(partition)} ]]")
                    partition_id = re.search(r"(\d+)", partition).group()

                    if 'y' == ask_user(f"Delete partition {disk.url}{partition_id} [y/N]:").lower():
                        SpawnedSU.do(f"sgdisk --delete={partition_id} {disk.url}")
                        print(f" * Partition {disk.url}{partition_id} DELETED", end="\n\n")

    def prepare_partitions(self):
        self.free_space_on_disks()
        self.scheme.execute(Create(system_label=self.op.L))
        self.scheme.execute(Format())
