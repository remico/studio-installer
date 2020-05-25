#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import LUKS, Container, LVM

__all__ = ['LvmOnLuksVG']


class LvmOnLuksVG(LUKS, Container, LVM):
    def __init__(self, vg, id_, **kwargs):
        super().__init__(id_=id_, vg=vg, **kwargs)

    def _a_execute(self, action):
        action.serve_lvm_on_luks_vg(self)
