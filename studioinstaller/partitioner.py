#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Manipulates partitions """

__author__ = 'remico <remicollab@gmail.com>'

from .partition.base import Partition, LVM, URL_DISK
from .partition import LvmLV
from .scheme import Scheme
from .spawned import ask_user, logger as log

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
            assert not isinstance(pt, LVM) or pt.lvm_vg, "No LVM VG is defined for an LVM LV"
            assert not pt.disk or pt.disk == URL_DISK(pt.id), "The disk value doesn't match to the partition id"
            assert not pt.islvm or pt.lvm_vg in LvmLV.groups(self.scheme), "LVM VGs do not match"

    def prepare_partitions(self):
        for pt in self.scheme:
            pt.serve()
