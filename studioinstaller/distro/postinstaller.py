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

from abc import abstractclassmethod, ABC

from ..runtimeconfig import RuntimeConfig
from ..mounter import Mounter

__all__ = ['PostInstaller']


class PostInstaller(ABC):
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self.scheme = runtime_config.scheme
        self.chroot = runtime_config.op.chroot
        self.disk = runtime_config.disk
        self.mounter = Mounter(self.chroot, self.scheme)

    def execute(self):
        self._run()

    @abstractclassmethod
    def _run(self):
        pass

    @abstractclassmethod
    def inject_tool(self, extras=False, develop=False):
        pass
