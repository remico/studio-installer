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

import yaml
from pathlib import Path

from .configfilebase import ConfigFileBase
from .. import util

__all__ = ['YamlConfig']

_tlog = util.tagged_logger('YamlConfig')


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
