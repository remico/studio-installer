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

from .osinstaller import OsInstaller
from .postinstaller import PostInstaller

from .ubuntu.ubuntuinstaller import UbuntuInstaller
from .ubuntu.ubuntupostinstaller import UbuntuPostInstaller

from .manjaro.manjaroinstaller import ManjaroInstaller
from .manjaro.manjaropostinstaller import ManjaroPostInstaller

from .. import util

__all__ = ['DistroFactory']


class DistroFactory:
    distro_name = util.distro_name().lower()

    @staticmethod
    def getInstaller(scheme) -> OsInstaller:
        if "ubuntu" in DistroFactory.distro_name:
            return UbuntuInstaller(scheme)
        elif "manjaro" in DistroFactory.distro_name:
            return ManjaroInstaller(scheme)

    @staticmethod
    def getPostInstaller(scheme, op, target_disk) -> PostInstaller:
        if "ubuntu" in DistroFactory.distro_name:
            return UbuntuPostInstaller(scheme, target_disk, op.chroot)
        elif "manjaro" in DistroFactory.distro_name:
            return ManjaroPostInstaller(scheme, target_disk, op.chroot)
