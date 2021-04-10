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

"""Useful functions"""

from time import sleep
from spawned import logger, create_py_script


__all__ = [
           'tagged_logger',
           'package_name',
           'cmd_edit_inplace',
           'delay',
           ]


def tagged_logger(tag: str):
    @logger.tagged(tag, logger.ok_blue_s)
    def _p(*text: str):
        return text
    return _p


def package_name():
    """Top-level package name"""
    return str(__package__).split('.')[0]


_edit_inplace_script = create_py_script(r"""
import fileinput
import re, sys

_a = sys.argv
filepath = _a[1]
re_pattern = _a[2]
replacement = _a[3]

with fileinput.FileInput(filepath, inplace=True) as f:
    for line in f:
        print(re.sub(re_pattern, replacement, line), end='')
""")


def cmd_edit_inplace(filepath: str, re_old: str, str_new: str):
    return f'python3 "{_edit_inplace_script}" "{filepath}" "{re_old}" "{str_new}"'


def delay(sec):
    print("waiting for the OS installer finishes the job...")
    for i in range(sec):
        print(i)
        sleep(1)
    print()
