#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .partitionbase import Partition

__all__ = ['Container']


class Container(Partition):
    @property
    def iscontainer(self):
        return True
