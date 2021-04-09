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
#  Copyright (c) 2020 remico

"""Ubuntu Studio semi-automatic installer:
    - create/change partitions map
    - encrypt partitions
    - configure lvm
    - install OS
    - mount/unmount encrypted partitions
    - configure the newly installed OS
"""

from importlib.metadata import version as app_version
from sys import exit as app_exit

from spawned import SpawnedSU, Spawned, ask_user, SETENV, logger

from .argparser import *
from .disksmounthelper import DisksMountHelper
from .distro import DistroFactory
from .mounter import Mounter
from .pluginloader import PluginLoader
from .preinstaller import PreInstaller
from .runtimeconfig import RuntimeConfig

from . import partitioning
from . import util

PLUGIN_API = '1.0'


def select_target_disk():
    SpawnedSU.do(r"parted -ls 2>/dev/null | egrep --color 'Disk\s+/dev|[kMG\d]B\s|Size'")
    return ask_user("Select target disk:")


def handle_subcmd_default(conf):
    mounter = Mounter(conf.op.chroot, conf.scheme)
    distrofactory = DistroFactory.instance()

    if conf.op.hard:
        mounter.unmount_target_system()

    if not conf.op.n:
        # unused; just prevents partitions automounting during the OS installation
        do_not_automount_new_partitions = DisksMountHelper()

        preinstaller = PreInstaller(conf.scheme, conf.op)
        preinstaller.prepare_partitions()

        os_installer = distrofactory.getInstaller(conf)
        os_installer.execute()

    # wait a little; target OS partitions get unmounted
    util.delay(5)

    if not conf.op.N:
        if util.target.ready_for_postinstall(conf.op.chroot):
            # do mandatory post-installation actions
            postinstaller = distrofactory.getPostInstaller(conf)
            postinstaller.execute()

            # install the tool into the target OS so that it will be available after reboot
            if conf.op.inject is not None:
                # NOTE: magic values, defined by argparser setup
                postinstaller.inject_tool(extras='extra' in conf.op.inject,
                                          develop='devel' in conf.op.inject)
        else:
            logger.warning("It looks like the target system is not ready for post-installation actions. "
                        "Trying to unmount the whole partitioning scheme and exit.")
            mounter.unmount_target_system()


def handle_subcmd_scheme(conf):
    mounter = Mounter(conf.op.mount or conf.op.chroot, conf.scheme)

    if conf.op.mount:
        mounter.mount_target_system()
        app_exit()

    if conf.op.umount or conf.op.hard:
        mounter.unmount_target_system()
        conf.op.umount and app_exit()  # exit if this option specified


def main():
    Spawned.enable_logging()

    argparser = ArgParser(__package__)
    argparser.set_subcommand_handler(SUBCMD_DEFAULT, handle_subcmd_default)
    argparser.set_subcommand_handler(SUBCMD_SCHEME, handle_subcmd_scheme)

    plugin_loader = PluginLoader(PLUGIN_API)
    plugin_loader.extend_argparser(argparser)

    argparser.register_plugins(plugin_loader)

    op = argparser.parse()

    # set password before one needs it
    if op.p:
        SETENV("UPASS", op.p)

    if op.d:
        Spawned.enable_debug_commands()

    if op.selftest:
        # TODO check required linux commands, .seed file, ubiquity, ubiquity.desktop file, partman, debconf database
        app_exit()

    if op.version:
        print(app_version(__package__))
        app_exit()

    target_disk = select_target_disk()
    scheme = partitioning.scheme(target_disk)
    runtime_config = RuntimeConfig(PLUGIN_API, target_disk, scheme, op)

    # call a bound function (defined by argparser)
    op.func(runtime_config)


if __name__ == '__main__':
    main()
