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

from spawned import ask_user, ENV

from _typing import StringEnum

from .partitionbase import Partition


__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['LUKS', 'LuksType']


class LuksType(StringEnum):
    luks1 = "luks1"
    luks2 = "luks2"


class LUKS(Partition):
    def __init__(self, type=LuksType.luks2, passphrase=None, **kwargs):
        super().__init__(**kwargs)
        self._passphrase = passphrase or ENV("LUKSPASS")
        self._type = type

    @property
    def passphrase(self):
        if not self._passphrase:
            self._passphrase = ask_user(f"Enter LUKS passphrase for '{self.url}':")
        return self._passphrase

    @property
    def mapperID(self):
        # FIXME replace the magic attribute with a descriptor or use another more clear way
        return getattr(self, '_evaluated_mapper_id', None)  # warning: magic attribute

    @property
    def luks_type(self):
        return self._type
