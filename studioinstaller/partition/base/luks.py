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

"""Partitions hierarchy"""

from spawned import ask_user, ENV

from _typing import StringEnum

from .partitionbase import Partition


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
