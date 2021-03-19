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

__all__ = ['ManjaroPostInstaller']


class ManjaroPostInstaller(PostInstaller):
    def _run(self):
        self.mounter.mount_target_system()

        # do useful stuff here

        self.mounter.unmount_target_system()

    def inject_tool(self, extras=False, develop=False):
        self.mounter.mount_target_system()

        # install the tool into the target OS

        self.mounter.unmount_target_system()
