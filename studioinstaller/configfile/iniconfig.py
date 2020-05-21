#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of "Ubuntu Studio Installer" project

#  Copyright (c) 2020, REMICO
#
#  The software is provided "as is", without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose and non-infringement. In no event shall the
#  authors or copyright holders be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.

"""INI-like config files handler"""

from pathlib import Path

from .configfilebase import ConfigFileBase
from .. import util

__all__ = ['IniConfig']


_tlog = util.tagged_logger('[IniConfig]')


class IniConfig(ConfigFileBase):
    def replace(self, re_old: str, str_new: str):
        if not Path(self.abs_filepath).exists():
            _tlog(f"File '{self.abs_filepath}' doesn't exist. No replacement done.")
            return

        cmd = util.cmd_edit_inplace(self.filepath, re_old, str_new)
        self._execute(cmd)
