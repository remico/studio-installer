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

"""Partitions hierarchy"""

from .partitionbase import Partition
from ...spawned import SpawnedSU, Spawned

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PV']


class PV(Partition):
    @property
    def isphysical(self):
        return True

    def create(self, t: Spawned = None):
        locally = not t
        if locally:
            t = SpawnedSU(f"gdisk {self.disk}")

        if self.is_new:
            basic_prompt = "Command (? for help)"
            t.interact(basic_prompt, "n")
            t.interact("Partition number", self._id if str(self._id).isdigit() else Spawned.ANSWER_DEFAULT)
            t.interact("First sector", Spawned.ANSWER_DEFAULT)
            t.interact("Last sector", f"+{self.size}" if self.size else Spawned.ANSWER_DEFAULT)
            t.interact("Hex code or GUID", self.type or Spawned.ANSWER_DEFAULT)

        if locally:
            t.interact("Command (? for help)", "w")
            t.interact("proceed?", "Y")
            t.waitfor(Spawned.TASK_END)
