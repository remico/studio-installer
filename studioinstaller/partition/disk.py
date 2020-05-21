#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Hardware medium """

__author__ = 'remico <remicollab@gmail.com>'

from .base import MediumBase, URL_DISK
from ..spawned import SpawnedSU

__all__ = ['Disk']


class Disk(MediumBase):
    def __init__(self, id_, **kwargs):
        super().__init__(id_=id_, **kwargs)

    def create_new_partition_table(self):
        basic_prompt = "Command (? for help)"
        with SpawnedSU(f"gdisk {self.url}") as t:
            t.interact(basic_prompt, "o")
            t.interact("Proceed?", "Y")
            t.interact(basic_prompt, "w")
            t.interact("proceed?", "Y")

    def do_serve(self):
        if brandnew := True:
            self.create_new_partition_table()

    @property
    def url(self):
        return URL_DISK(self.id)
