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

"""Encapsulates a partitioning scheme"""

from typing import List
from .partition.base import Partition

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['Scheme']


class Scheme:
    def __init__(self, partitions: List[Partition] = None):
        self.scheme = partitions

    def __iter__(self):
        return self.scheme.__iter__()

    def add(self, pt: Partition):
        self.scheme.append(pt)

    def partitions(self, *types, new=None) -> List[Partition]:
        return [pt for pt in self.scheme if all(isinstance(pt, T) for T in types)
                and (pt.is_new == new if new is not None else True)]

    def partition(self, mountpoint) -> Partition:
        return next((pt for pt in self.scheme if mountpoint in pt.mountpoint), None)

    def execute(self, action):
        for pt in action.iterator(self):
            pt.execute(action)
