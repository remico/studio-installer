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
from .partmancheater import PartmanCheater, MountPreventer
from .pluginsloader import PluginsLoader
from .preinstaller import PreInstaller
from .postinstaller import PostInstaller

from . import partitioning
from . import util


def run_os_installation():
    if "ubuntu" in util.distro_name().lower():
        if seed_file := util.preseeding_file():
            SpawnedSU.do(f"debconf-set-selections {seed_file}")

    # parse the .desktop file to get the installation command; grep for 'ubiquity' to filter other .desktop files if any
    data = Spawned.do("grep '^Exec' ~/Desktop/*.desktop | grep 'ubiquity' | tail -1 | sed 's/^Exec=//'")
    cmd = data.replace("ubiquity", "ubiquity -b --automatic")
    Spawned(cmd).waitfor(Spawned.TASK_END, timeout=Spawned.TIMEOUT_INFINITE)


def select_target_disk():
    SpawnedSU.do(r"parted -ls | egrep --color 'Disk\s+/dev|[kMG\d]B\s|Size'")
    return ask_user("Select target disk:")


def handle_subcmd_default(op, scheme, postinstaller, **kwargs):
    if not op.n:
        util.clear_installation_cache()

        # unused; just prevents partitions automounting during the OS installation
        do_not_automount_new_partitions = MountPreventer()

        preinstaller = PreInstaller(scheme)
        preinstaller.prepare_partitions()

        # wait for Partman and modify values in background
        PartmanCheater(scheme).run()

        run_os_installation()

    if util.ready_for_postinstall(op.chroot):
        # do mandatory post-installation actions
        postinstaller.run()

        # install the tool into target OS (will be available after reboot)
        if op.inject is not None:
            # NOTE: magic values, defined by argparser setup
            postinstaller.inject_tool(extras='extra' in op.inject,
                                      develop='devel' in op.inject)
    else:
        logger.warning("It looks like the target system is not ready for post-installation actions. "
                       "Trying to unmount the whole partitioning scheme and exit.")
        postinstaller.unmount_target_system()


def handle_subcmd_scheme(op, postinstaller, **kwargs):
    if op.mount:
        postinstaller.chroot = op.mount  # op.mount value takes precedence over op.chroot for 'mount' command
        postinstaller.mount_target_system()
        app_exit()

    if op.umount or op.hard:
        postinstaller.unmount_target_system()
        op.umount and app_exit()  # exit if this option specified


def main():
    Spawned.enable_logging()

    argparser = ArgParser(__package__)
    argparser.set_subcommand_handler(SUBCMD_DEFAULT, handle_subcmd_default)
    argparser.set_subcommand_handler(SUBCMD_SCHEME, handle_subcmd_scheme)

    plugins_loader = PluginsLoader()
    plugins_loader.extend_argparser(argparser)

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
    postinstaller = PostInstaller(scheme, target_disk, op.chroot)

    # call a bound function (defined by argparser)
    op.func(op, postinstaller=postinstaller, scheme=scheme)


if __name__ == '__main__':
    main()
