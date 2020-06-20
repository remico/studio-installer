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

"""Prepare partitions for OS installation according to the partitioning scheme"""

from spawned import ask_user, logger as log

from .action import Create, Format
from .partition.base import Partition, FS, URL_DISK
from .partition import LvmLV
from .scheme import Scheme
from .util import is_efi_boot

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Partitioner']


class Partitioner:
    def __init__(self, scheme: Scheme):
        self.scheme = scheme
        self.lukspass = ''

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
            assert not pt.islvmlv or pt.lvm_vg in LvmLV.groups(self.scheme), "LVM VGs do not match"
            assert not pt.do_format or isinstance(pt, FS), f"Partition {pt.id} can't be formatted"
            assert "efi" not in pt.mountpoint or is_efi_boot(), \
                "Partitioning scheme contains a EFI partition while the system doesn't look to booted in EFI mode"

    def prepare_partitions(self):
        for d in self.scheme.disks():
            # TODO support pre-existing partitions
            if may_clear_whole_disk := True:
                d.create_new_partition_table()
        self.scheme.execute(Create())
        self.scheme.execute(Format())
