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

"""Abstract action interface"""

from abc import ABC, abstractmethod
from typing import List, Union, final
from ..partition.base import MediumBase

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

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
