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

import yaml
from pathlib import Path

from .configfilebase import ConfigFileBase
from .. import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['YamlConfig']

_tp = util.tagged_printer('YamlConfig')


class YamlConfig(ConfigFileBase):
    def __init__(self, filepath, chroot_context=None):
        super().__init__(filepath, chroot_context)
        self._load()

    def __getattr__(self, name):
        return self._yaml and self._yaml[name]

    def is_valid(self):
        return bool(self._yaml)

    def replace(self, re_old: str, str_new: str):
        raise NotImplementedError(f"{__class__.__name__}.replace() method is not implemented")

    def append(self, str_new: str):
        raise NotImplementedError(f"{__class__.__name__}.append() method is not implemented")

    def _load(self):
        path = self.abs_filepath
        if not path or not Path(path).exists():
            return

        with open(path) as f:
            self._yaml = yaml.safe_load(f)

        return self._yaml
