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

"""Hardware medium"""

from .base import MediumBase, URL_DISK
from ..spawned import SpawnedSU

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

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

    def _a_execute(self, action):
        action.serve_disk(self)

    @property
    def url(self):
        return URL_DISK(self.id)
