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

"""In combination with __future__.annotations, provides ability for IDE
to perform type checking.

Usage:
at the top of a python module add::

    from __future__ import annotations
    from _typing import *

"""

from typing import TYPE_CHECKING, final


if TYPE_CHECKING:
    # builtin
    from typing import List, Tuple, Iterable, Iterator

    # top-level module
    from preinstaller import *
    from scheme import *
    from postinstaller import *

    # inner modules
    from spawned import *

    from studioinstaller.action import *
    from studioinstaller.action.actionbase import *
    from studioinstaller.partition import *
    from studioinstaller.partition.base import *
