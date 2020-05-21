#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import LUKS, FS

__all__ = ['EncryptedPV']


class EncryptedPV(LUKS, FS):
    def __init__(self, id_, mountpoint=''):
        super().__init__(id_=id_, mountpoint=mountpoint)

    def do_serve(self):
        pass
