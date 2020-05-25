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

""" Abstract action interface """

from abc import ABC, abstractmethod

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['ActionBase']


class ActionBase(ABC):
    @abstractmethod
    def iterator(self, scheme):
        pass

    @abstractmethod
    def serve_disk(self, disk):
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
