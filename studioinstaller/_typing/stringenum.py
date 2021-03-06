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

"""Returns string values instead of keys"""

from enum import Enum

__all__ = ['StringEnum']


class StringEnum(Enum):
    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()
