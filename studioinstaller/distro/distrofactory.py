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

from ..runtimeconfig import RuntimeConfig

from .osinstaller import OsInstaller
from .postinstaller import PostInstaller

from .manjaro.manjarodistrofactory import ManjaroDistroFactory
from .ubuntu.ubuntudistrofactory import UbuntuDistroFactory

from .. import util

__all__ = ['DistroFactory']


class DistroFactory:

    @staticmethod
    def instance():
        distro_name = util.distro_name().lower()
        if "ubuntu" in distro_name:
            return UbuntuDistroFactory()
        elif "manjaro" in distro_name:
            return ManjaroDistroFactory()
        else:
            raise NotImplementedError(f"DistroFactory for '{distro_name}' distro is not supported")

    def getInstaller(self, runtime_config: RuntimeConfig) -> OsInstaller:
        pass

    def getPostInstaller(self, runtime_config: RuntimeConfig) -> PostInstaller:
        pass
