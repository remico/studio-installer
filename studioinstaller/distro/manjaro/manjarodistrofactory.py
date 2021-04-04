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

from ..distrofactory import DistroFactory

from .manjaroinstaller import ManjaroInstaller
from .manjaropostinstaller import ManjaroPostInstaller

__all__ = ['ManjaroDistroFactory']


class ManjaroDistroFactory(DistroFactory):

    def getInstaller(self, runtime_config: RuntimeConfig) -> ManjaroInstaller:
        return ManjaroInstaller(runtime_config)

    def getPostInstaller(self, runtime_config: RuntimeConfig) -> ManjaroPostInstaller:
        return ManjaroPostInstaller(runtime_config)
