#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Partitions hierarchy """

__author__ = 'remico <remicollab@gmail.com>'

from .partitionbase import Partition
from ...spawned import SpawnedSU, Spawned

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
