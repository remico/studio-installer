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

"""Encapsulates a partitioning scheme"""

from typing import List

from .partition.base import Partition
from .partition import Disk

__all__ = ['Scheme']


class Scheme:
    def __init__(self, partitions: List[Partition] = None):
        self.scheme = set()
        for pt in partitions:
            while pt := self._add_pt(pt):  # instead of recursive calls
                pass

        print("\n============= Partitions to be processed: =============")
        for pt in sorted(self.scheme, key=lambda p: len(p.url.split('/'))):
            print(f"{pt.__class__.__name__} :: {pt.url} :: {pt.mountpoint}")
        print("\n")

    def __iter__(self):
        return self.scheme.__iter__()

    def _add_pt(self, pt):
        if isinstance(pt, Partition):
            self.scheme.add(pt)
        return pt.parent

    def add(self, pt: Partition):
        assert isinstance(pt, Partition)
        self._add_pt(pt)

    def disks(self) -> List[Disk]:
        disks = {pt.parent for pt in self.scheme if isinstance(pt.parent, Disk)}
        return list(disks)

    def partitions(self, *types, new=None, disk=None) -> List[Partition]:
        """
        ``types`` - return only subclasses of the Partition class
        ``new`` - return only new partitions
        ``disk`` - return only partitions on this disk
        """
        types = types or (Partition,)
        return [pt for pt in self.scheme
                    if all(isinstance(pt, T) for T in types)
                        and (pt.disk == disk if disk is not None else True)
                        and (pt.is_new == new if new is not None else True)
                ]

    def execute(self, action):
        for pt in action.iterator(self):
            pt.execute(action)

    @property
    def boot_partition(self):
        for pt in self.scheme:
            if pt.mountpoint == "/boot":
                return pt
        return self.root_partition

    @property
    def root_partition(self):
        for pt in self.scheme:
            if pt.mountpoint == "/":
                return pt
