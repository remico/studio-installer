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

from .action import Create, Format, Encrypt
from .partition.base import Partition, LVM, FS, URL_DISK
from .partition import LvmLV
from .scheme import Scheme
from .spawned import ask_user, logger as log

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

        self.validate_scheme()

    @property
    def passphrase(self):
        return self.lukspass or ask_user("Enter LUKS passphrase:")

    def validate_scheme(self):
        assert self.scheme, "No partitioning scheme is defined"

        for pt in self.scheme:
            assert isinstance(pt, Partition), "Partitioning scheme must contain Partition's only"
            assert pt.is_new, "All partitions in the scheme must be marked as New"
            assert pt.parent, f"No parent specified for {pt.id}"
            assert not isinstance(pt, LVM) or pt.lvm_vg, "No LVM VG is defined for an LVM LV"
            assert not pt.do_format or isinstance(pt, FS), f"Partition {pt.id} can't be formatted"
            assert not pt.disk or pt.disk == URL_DISK(pt.id), "The disk value doesn't match to the partition id"
            assert not pt.islvm or pt.lvm_vg in LvmLV.groups(self.scheme), "LVM VGs do not match"

    def prepare_partitions(self):
        for d in self.scheme.disks():
            # TODO support pre-existing partitions
            if may_clear_whole_disk := True:
                d.create_new_partition_table()
        self.scheme.execute(Create())
        self.scheme.execute(Format())
