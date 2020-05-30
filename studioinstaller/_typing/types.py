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

"""In combination with __future__.annotations, provides ability for IDE
to perform type checking.

Usage:
at the top of a python module add::

    from __future__ import annotations
    from _typing import *

"""

from typing import TYPE_CHECKING, final

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"


if TYPE_CHECKING:
    # builtin
    from typing import List, Tuple, Iterable, Iterator

    # top-level module
    from partitioner import *
    from partmancheater import *
    from scheme import *
    from postinstaller import *

    # inner modules
    from spawned import *

    from studioinstaller.action import *
    from studioinstaller.action.actionbase import *
    from studioinstaller.partition import *
    from studioinstaller.partition.base import *
