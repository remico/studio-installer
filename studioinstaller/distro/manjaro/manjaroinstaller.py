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

from pathlib import Path
from importlib.metadata import files as app_files
from sys import exit as app_exit

from spawned import Spawned, SpawnedSU

from ..osinstaller import OsInstaller
from ...mounter import Mounter
from ... import util

__all__ = ['ManjaroInstaller']


_tlog = util.tagged_logger("[ManjaroInstaller]")

class ManjaroInstaller(OsInstaller):
    def _prepare_installation(self):
        # ensure setup script is installed
        if not SpawnedSU.do("which setup || pacman -S manjaro-architect --noconfirm", with_status=True).success:
            _tlog("manjaro-architect isn't available. Abort...")
            app_exit()

        Mounter(self.chroot, self.scheme).mount_target_system()

    def _setup_unattended_installation(self):
        if not Path("/etc/calamares").exists():
                return

        packagename = util.package_name()
        calamares_modules = [
            str(f.locate()) for f in app_files(packagename) if "calamares" in str(f) and str(f).endswith(".conf")
        ]
        if calamares_modules:
            SpawnedSU.do(f"mkdir -p /etc/calamares/modules && cp {' '.join(calamares_modules)} /etc/calamares/modules")

    def _begin_installation(self):
        if 0:  # calamares
            Spawned.do("/usr/bin/calamares_polkit", timeout=Spawned.TIMEOUT_INFINITE)
        else:  # manjaro architect
            t = SpawnedSU("setup", timeout=Spawned.TIMEOUT_INFINITE)
            t.interact_user()
            t.waitfor(SpawnedSU.TASK_END)
