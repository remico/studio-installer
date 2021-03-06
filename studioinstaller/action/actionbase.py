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

"""Abstract action interface"""

from abc import ABC, abstractmethod
from typing import List, Union, final
from ..partition.base import MediumBase

__all__ = ['ActionBase', '_sort_key']


def _sort_key(pt):
    if pt.iscontainer:  # LUKS, LVM VG/PV?
        return len(pt.url.split('/'))
    elif pt.mountpoint == "/":
        return 100
    elif pt.isswap:  # allocate swap next to the root partition
        return 101
    else:
        return 102 + len(pt.mountpoint.split('/'))


class ActionBase(ABC):
    def __init__(self, **kwargs):
        self.nodes: Union[List[MediumBase], None] = []
        self._extra_kw = kwargs

    @final
    def __iter__(self):  # for(...)
        return self

    def __next__(self):  # next()
        if self.nodes:
            return self.nodes.pop(0)
        raise StopIteration

    @abstractmethod
    def iterator(self, scheme):
        pass

    @abstractmethod
    def serve_standard_pv(self, pt):
        pass

    @abstractmethod
    def serve_luks_pv(self, pt):
        pass

    @abstractmethod
    def serve_lvm_on_luks_vg(self, pt):
        pass

    @abstractmethod
    def serve_lvm_lv(self, pt):
        pass

    @abstractmethod
    def serve_encrypted_vv(self, pt):
        pass
