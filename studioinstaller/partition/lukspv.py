#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .base import PV, Container, LUKS
from ..spawned import SpawnedSU

__all__ = ['LuksPV']


class LuksPV(LUKS, PV, Container):
    def __init__(self, id_):
        super().__init__(id_=str(id_))

    def encrypt(self, passphrase=None):
        if passphrase:
            self._passphrase = passphrase
        with SpawnedSU(f"cryptsetup luksFormat {self.url}") as t:
            t.interact("Type uppercase yes", "YES")
            t.interact("Enter passphrase for", self.passphrase)
            t.interact("Verify passphrase", self.passphrase)

    def do_serve(self):
        if self.is_new:
            self.create()
            self.encrypt()
