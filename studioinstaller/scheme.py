#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Contains all defined partitions in the partitioning scheme """

__author__ = 'remico <remicollab@gmail.com>'

from typing import List
from .partition.base import Partition


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
