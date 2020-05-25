#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import PV, FS

__all__ = ['StandardPV']


class StandardPV(PV, FS):
    def __init__(self, id_, mountpoint=''):
        super().__init__(id_=str(id_), mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_standard_pv(self)
