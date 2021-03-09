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

from spawned import Spawned, SpawnedSU

from .partmanhelper import PartmanHelper
from ..osinstaller import OsInstaller
from ... import util

__all__ = ['UbuntuInstaller']


class UbuntuInstaller(OsInstaller):
    def _prepare_installation(self):
        # clear partman cache
        SpawnedSU.do("rm -rf /var/lib/partman")

        # clear debconf cache
        # note: removing the DB leads the ubiquity installer to crash
        SpawnedSU.do_script("""
            if [ ! -d /var/cache/debconf.back ]; then
                cp -r /var/cache/debconf/ /var/cache/debconf.back
            else
                rm -rf /var/cache/debconf
                cp -r /var/cache/debconf.back /var/cache/debconf
            fi
            """)

        # wait for Partman and modify values in background
        PartmanHelper(self.scheme).run()

    def _setup_unattended_installation(self):
        if seed_file := util.preseeding_file():
            SpawnedSU.do(f"debconf-set-selections {seed_file}")

    def _begin_installation(self):
        # parse the .desktop file to get the installation command; grep for 'ubiquity' to filter other .desktop files if any
        data = Spawned.do("grep '^Exec' ~/Desktop/*.desktop | grep 'ubiquity' | tail -1 | sed 's/^Exec=//'")
        cmd = data.replace("ubiquity", "ubiquity -b --automatic")
        Spawned(cmd).waitfor(Spawned.TASK_END, timeout=Spawned.TIMEOUT_INFINITE)
