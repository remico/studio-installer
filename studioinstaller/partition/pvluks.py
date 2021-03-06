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

from .base import PV, Container, LUKS, LuksType

__all__ = ['PVLuks']


class PVLuks(LUKS, PV, Container):
    def __init__(self, id_, type=LuksType.luks2):
        super().__init__(type=type, id_=str(id_))

    def _a_execute(self, action):
        action.serve_luks_pv(self)
