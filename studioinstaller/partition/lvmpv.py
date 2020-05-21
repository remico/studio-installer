#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import PV, Container, LVM

__all__ = ['LvmPV']


class LvmPV(PV, Container, LVM):
    pass
