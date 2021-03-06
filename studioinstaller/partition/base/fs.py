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

from .partitionbase import Partition

__all__ = ['FS']


class FS(Partition):
    def makefs(self, fs=''):
        self.do_format = True
        self.fs = fs.lower()
        return self
