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

from spawned import onExit, SpawnedSU, Spawned

__all__ = ['DisksMountHelper']

class DisksMountHelper:
    """Temporarily disables ``udisksd`` service in order to prevent auto-mounting of newly created partitions"""

    daemon_active = None

    def __init__(self):
        DisksMountHelper.daemon_active = self.is_daemon_active()
        if DisksMountHelper.daemon_active:
            SpawnedSU.do("systemctl stop udisks2.service")
            print("udisks2.service stopped")

    def __del__(self):
        self.on_exit()

    @staticmethod
    def is_daemon_active():
        return Spawned.do(
                "systemctl status udisks2.service | grep '(running)'", with_status=True
            )[0] == 0

    @staticmethod
    def on_exit():
        if DisksMountHelper.daemon_active and not DisksMountHelper.is_daemon_active():
            SpawnedSU.do("systemctl start udisks2.service")
            print("udisks2.service started")


onExit(lambda: DisksMountHelper.on_exit())
