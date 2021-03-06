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

from .base import PV, FS

__all__ = ['PVPlain']


class PVPlain(PV, FS):
    def __init__(self, id_, mountpoint=''):
        super().__init__(id_=str(id_), mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_standard_pv(self)
