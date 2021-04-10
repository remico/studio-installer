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
#  Copyright (c) 2021 remico

from dataclasses import dataclass

from .argparser import ArgParser
from .scheme import Scheme

__all__ = ['RuntimeConfig']


@dataclass
class RuntimeConfig:
    plugin_api: int
    disk: str
    scheme: Scheme
    op: ArgParser
