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

from ..postinstaller import PostInstaller
from ...runtimeconfig import RuntimeConfig

__all__ = ['ManjaroPostInstaller']


class ManjaroPostInstaller(PostInstaller):
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self.scheme = runtime_config.scheme
        self.chroot = runtime_config.op.chroot
        self.bl_disk = runtime_config.disk

    def _run(self):
        self.mount_target_system()

        # do useful stuff here

        self.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mount_target_system()

        # install the tool into the target OS

        self.unmount_target_system()
