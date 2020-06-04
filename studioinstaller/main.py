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

from spawned import SpawnedSU, Spawned, ask_user, SETENV

from .action import Release, Involve
from .partition.base import VType
from .partition import Disk, StandardPV, LuksPV, LvmOnLuksVG, LvmLV
from .partitioner import Partitioner
from .partmancheater import PartmanCheater
from .postinstaller import PostInstaller
from .scheme import Scheme

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"


def run_os_installation():
    SpawnedSU.do(f"debconf-set-selections {preseeding_file()}")

    # parse the .desktop file to get the installation command
    # warning: in case of multiple .desktop files are in ~/Desktop dir, returns the last found 'Exec=...' value
    data = Spawned.do("grep '^Exec' ~/Desktop/*.desktop | tail -1 | sed 's/^Exec=//'")
    cmd = data.replace("ubiquity", "ubiquity -b --automatic")
    Spawned(cmd).waitfor(Spawned.TASK_END, timeout=Spawned.TO_INFINITE)


def preseeding_file():
    # TODO move .seed file inside the package and use resource API
    from importlib.metadata import files as app_files
    if l := [f for f in app_files(__package__) if '.seed' in str(f)]:
        return l[0].locate()


def clear_installation_cache():
    # clear partman cache
    SpawnedSU.do("rm -rf /var/lib/partman")
    # clear debconf cache
    # FIXME removing the DB leads the ubiquity installer to crash
    # SpawnedSU.do("rm -rf /var/cache/debconf")
    SpawnedSU.do_script("""
        if [ ! -d /var/cache/debconf.back ]; then
            cp -r /var/cache/debconf/ /var/cache/debconf.back
        else
            rm -rf /var/cache/debconf
            cp -r /var/cache/debconf.back /var/cache/debconf
        fi
        """)


def select_target_disk():
    SpawnedSU.do(r"parted -l | egrep --color 'Disk\s+/dev|[kMG\d]B\s|Size'")
    return ask_user("Select target disk:")


def parse_cmd_options():
    argparser = argparse.ArgumentParser(prog=__package__)
    argparser.add_argument("--hard", action="store_true",
                           help="Deactivates LVM volumes and target swap, unmounts target filesystems"
                                " and closes encrypted LUKS devices before the script starts")
    argparser.add_argument("-p", type=str, metavar="PASSWORD", help="User password")
    argparser.add_argument("-d", action="store_true", help="Enable commands debug output")
    argparser.add_argument("--version", action="store_true", help="Show version and exit")
    argparser.add_argument("--selftest", action="store_true", help="Check environment and own resources and exit")

    DEFAULT_CHROOT = "/target"

    mount_opts = argparser.add_mutually_exclusive_group()
    mount_opts.add_argument("--mount", type=str, const=DEFAULT_CHROOT, metavar="ROOT", nargs='?',
                            help=f"Mount the whole scheme and exit (Default ROOT: {DEFAULT_CHROOT})")
    mount_opts.add_argument("--umount", action="store_true", help="Unmount the whole scheme and exit")

    mount_opts.add_argument("--chroot", type=str, default=DEFAULT_CHROOT,
                            help=f"Target system's mountpoint (Default: {DEFAULT_CHROOT})")

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

    clear_installation_cache()
    target_disk = select_target_disk()

    # =======================================
    # ========= PARTITIONING SCHEME =========
    # =======================================
    disk1 = Disk(target_disk)

    # edit partitioning configuration according to your needs
    p1 = StandardPV(1, '/boot/efi').new("100M", VType.EFI).on(disk1).makefs()
    p2 = LuksPV(2).new().on(disk1)
    lvm_vg = LvmOnLuksVG('vg', 'cryptlvm').new().on(p2)
    root = LvmLV('root', '/').new("15G").on(lvm_vg).makefs('ext4')
    swap = LvmLV('swap', 'swap').new("1G", VType.SWAP).on(lvm_vg)
    home = LvmLV('home', '/home').new("100%FREE").on(lvm_vg).makefs('ext4')

    scheme = Scheme([p1, p2, lvm_vg, root, swap, home])
    # ================= END =================

    if op.hard:
        scheme.execute(Release())

    if op.mount:
        scheme.execute(Involve(chroot=op.mount))
        app_exit()

    if op.umount:
        scheme.execute(Release())
        app_exit()

    # partitioner = Partitioner(scheme)
    # partitioner.prepare_partitions()
    #
    # # wait for Partman and cheat it
    # PartmanCheater(scheme).run()
    #
    # run_os_installation()

    postinstaller = PostInstaller(scheme, target_disk, chroot=op.chroot)
    postinstaller.run()


if __name__ == '__main__':
    run()
