#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of "Ubuntu Studio Installer" project
#
#  Copyright (c) 2020, REMICO
#
#  The software is provided "as is", without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose and non-infringement. In no event shall the
#  authors or copyright holders be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.

"""Ubuntu Studio semi-automatic installer:
    - create/change partitions map
    - encrypt partitions
    - configure lvm
    - install OS
    - mount/unmount encrypted partitions
    - configure the newly installed OS
"""

import argparse
from importlib.metadata import version as app_version
from sys import exit as app_exit

from spawned import SpawnedSU, Spawned, ask_user, SETENV, logger

from .partmancheater import PartmanCheater, MountPreventer
from .preinstaller import PreInstaller
from .postinstaller import PostInstaller
from .postextra import run_postextra

from . import partitioning
from . import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

SUBCMD_SCHEME = "scheme"
SUBCMD_EXTRA = "extra"
SUBCMD_DEFAULT = "default"


def run_os_installation():
    SpawnedSU.do(f"debconf-set-selections {util.preseeding_file()}")

    # parse the .desktop file to get the installation command
    # warning: in case of multiple .desktop files are in ~/Desktop dir, returns the last found 'Exec=...' value
    data = Spawned.do("grep '^Exec' ~/Desktop/*.desktop | tail -1 | sed 's/^Exec=//'")
    cmd = data.replace("ubiquity", "ubiquity -b --automatic")
    Spawned(cmd).waitfor(Spawned.TASK_END, timeout=Spawned.TO_INFINITE)


def select_target_disk():
    SpawnedSU.do(r"parted -l | egrep --color 'Disk\s+/dev|[kMG\d]B\s|Size'")
    return ask_user("Select target disk:")


def subcmd_default(op, scheme, postinstaller, **kwargs):
    if not op.n:
        util.clear_installation_cache()

        do_not_automount_new_partitions = MountPreventer()

        preinstaller = PreInstaller(scheme)
        preinstaller.prepare_partitions()

        # wait for Partman and modify values in background
        PartmanCheater(scheme).run()

        run_os_installation()

    if util.ready_for_postinstall(op.chroot):
        postinstaller.run(op.epost)
    else:
        logger.warning("It looks like the target system is not ready for post-installation actions. "
                       "Trying to unmount the whole partitioning scheme and exit.")
        postinstaller.unmount_target_system()


def subcmd_scheme(op, postinstaller, **kwargs):
    if op.mount:
        postinstaller.chroot = op.mount  # op.mount value takes precedence over op.chroot for 'mount' command
        postinstaller.mount_target_system()
        app_exit()

    if op.umount or op.hard:
        postinstaller.unmount_target_system()
        op.umount and app_exit()  # exit if this option specified


def subcmd_extra(**kwargs):
    run_postextra()
    app_exit()


def parse_cmd_options():
    argparser = argparse.ArgumentParser(prog=__package__)

    # main command options
    argparser.add_argument("--hard", action="store_true",
                           help="Deactivates LVM volumes and target swap, unmounts target filesystems"
                                " and closes encrypted LUKS devices before the script starts")
    argparser.add_argument("-p", type=str, metavar="PASSWORD", help="User password")
    argparser.add_argument("-d", action="store_true", help="Enable commands debug output")
    argparser.add_argument("--version", action="store_true", help="Show version and exit")
    argparser.add_argument("--selftest", action="store_true", help="Check environment and own resources and exit")

    DEFAULT_CHROOT = "/target"
    argparser.add_argument("--chroot", type=str, default=DEFAULT_CHROOT,
                           help=f"Target system's mountpoint (Default: {DEFAULT_CHROOT})")

    argparser.add_argument("-n", action="store_true",
                           help="Skip disk partitioning and OS installation steps, run default post-install steps only")
    argparser.add_argument("--epost", action="store_true",
                           help="Schedule extra post-install steps which will be performed on user's first GUI login")

    # register sub-commands
    subcmd_parser = argparser.add_subparsers(dest="sub_cmd",
                                             description="Set of commands for extra functionality")
    # default sub-command values, in order SUBCMD_DEFAULT sub-command name can be omitted
    argparser.set_defaults(sub_cmd=SUBCMD_DEFAULT, func=subcmd_default)

    # default command
    subcmd_parser.add_parser(SUBCMD_DEFAULT, help="Default command, it implies if no other commands specified")

    # mount/umount
    scheme_argparser = subcmd_parser.add_parser(SUBCMD_SCHEME, help="Actions on the partitioning scheme")
    scheme_argparser.set_defaults(func=subcmd_scheme)
    mount_opts = scheme_argparser.add_mutually_exclusive_group()
    mount_opts.add_argument("--mount", type=str, const=DEFAULT_CHROOT, metavar="ROOT", nargs='?',
                            help=f"Mount the whole partitioning scheme and exit (Default ROOT: {DEFAULT_CHROOT})")
    mount_opts.add_argument("--umount", action="store_true", help="Unmount the whole partitioning scheme and exit")

    # extra steps upon GUI login
    extra_argparser = subcmd_parser.add_parser(SUBCMD_EXTRA, help="Run extra post-install steps only")
    extra_argparser.set_defaults(func=subcmd_extra)

    return argparser.parse_args()


def run():
    Spawned.enable_logging()

    op = parse_cmd_options()

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
    postinstaller = PostInstaller(scheme, target_disk, chroot=op.chroot)

    op.func(op=op, postinstaller=postinstaller, scheme=scheme)


if __name__ == '__main__':
    run()
