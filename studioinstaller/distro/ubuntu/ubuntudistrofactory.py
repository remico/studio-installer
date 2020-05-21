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

from ...runtimeconfig import RuntimeConfig

from ..distrofactorybase import DistroFactoryBase

from .ubuntuinstaller import UbuntuInstaller
from .ubuntupostinstaller import UbuntuPostInstaller

__all__ = ['UbuntuDistroFactory']


class UbuntuDistroFactory(DistroFactoryBase):

    def getInstaller(self, runtime_config: RuntimeConfig) -> UbuntuInstaller:
        return UbuntuInstaller(runtime_config)

    def getPostInstaller(self, runtime_config: RuntimeConfig) -> UbuntuPostInstaller:
        return UbuntuPostInstaller(runtime_config)
