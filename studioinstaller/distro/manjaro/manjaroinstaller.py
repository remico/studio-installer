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

from spawned import Spawned, SpawnedSU

from ..osinstaller import OsInstaller

__all__ = ['ManjaroInstaller']


class ManjaroInstaller(OsInstaller):
    def _prepare_installation(self):
        pass

    def _setup_unattended_installation(self):
        if not Path("/etc/calamares").exists():
                return

        packagename = str(__package__).split('.')[0]  # top-level package name
        calamares_modules = [
            str(f.locate()) for f in app_files(packagename) if "calamares" in str(f) and str(f).endswith(".conf")
        ]
        if calamares_modules:
            SpawnedSU.do(f"mkdir -p /etc/calamares/modules && cp {' '.join(calamares_modules)} /etc/calamares/modules")

    def _begin_installation(self):
        # Spawned.do("/usr/bin/calamares_polkit", timeout=Spawned.TIMEOUT_INFINITE)
        SpawnedSU.do("setup", timeout=Spawned.TIMEOUT_INFINITE)
