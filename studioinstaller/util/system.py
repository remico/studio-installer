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

import os
import stat

from spawned import Spawned

__all__ = [
    'uefi_loaded',
    'distro_name',
    'os_stat',
    'is_readable',
    'is_editable',
    'owner_uid',
]


def uefi_loaded():
    return Spawned.do("mount | grep efivars", with_status=True).success


def distro_name():
    return Spawned.do("less /etc/lsb-release | grep -oP '(?<=DISTRIB_ID=).*'")


def os_stat(path: str):
    return os.stat(path)


def is_readable(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return bool(statinfo_or_path.st_mode & (stat.S_IRUSR | stat.S_IRGRP))


def is_editable(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return bool(statinfo_or_path.st_mode & (stat.S_IWUSR | stat.S_IWGRP))


def owner_uid(statinfo_or_path):
    if not isinstance(statinfo_or_path, os.stat_result):
        statinfo_or_path = os_stat(statinfo_or_path)
    return statinfo_or_path.st_uid
