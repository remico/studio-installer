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

"""Hardware medium"""

from spawned import SpawnedSU
from .base import MediumBase, URL_DISK

__all__ = ['Disk']


class Disk(MediumBase):
    def __init__(self, id_, **kwargs):
        super().__init__(id_=id_.replace('/dev/', ''), **kwargs)

    def create_new_partition_table(self):
        basic_prompt = "Command (? for help)"
        with SpawnedSU(f"gdisk {self.url}") as t:
            t.interact(basic_prompt, "o")
            t.interact("Proceed?", "Y")
            t.interact(basic_prompt, "w")
            t.interact("proceed?", "Y")

    @property
    def url(self):
        return URL_DISK(self.id)
