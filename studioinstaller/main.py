#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" OS Linux semi-automatic installer:
    - create/change partitions map
    - encrypt the partitions
    - configure lvm
    - install OS
    - mount/unmount encrypted partitions
    - configure the newly installed OS
"""

__author__ = 'remico <remicollab@gmail.com>'

import argparse
from pathlib import Path
from .partition.base import VType
from .partition import Disk, StandardPV, LuksPV, LvmOnLuksVG, LvmLV
from .partitioner import Partitioner
from .partmancheater import PartmanCheater
from .postinstaller import PostInstaller
from .scheme import Scheme
from .spawned import SpawnedSU, Spawned, ask_user, SETENV


def hard_cleanup():
    # FIXME magic words
    # SpawnedSU.do(f"swapoff /dev/mapper/{vg_name}-{swap}")

    # hardcode:
    # - implies chroot in /target
    # - implies only one lvm vg
    # - closes all luks devices
    # - disables all active swaps
    SpawnedSU.do_script(r"""
        swapoff -a
        umount /target/boot/efi
        VG=$(sudo vgscan | grep -oP '(?<=\").*(?=\")')
        echo "@@ LVM VG >>> $VG"
        umount /dev/mapper/$VG-*
        vgchange -a n $VG
        find /dev/mapper -type l | xargs cryptsetup close --
    """)


def run_os_installation():
    # FIXME change path to /cdrom/ubuntustudio.seed
    SpawnedSU.do("debconf-set-selections $(find /home -name *.seed)")

    # parse the .desktop file to get the installation command
    data = Spawned.do("grep '^Exec' ~/Desktop/*.desktop | tail -1 | sed 's/^Exec=//'")
    cmd = data.replace("ubiquity", "ubiquity -b --automatic")
    Spawned(cmd).waitfor(Spawned.TASK_END, timeout_s=Spawned.TO_INFINITE)


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
    return ask_user("Select target disk:").replace('/dev/', '')


def run():
    Spawned.enable_logging()

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--hard", action="store_true",
                           help="Deactivates LVM volumes and target swap, unmounts target filesystems"
                                " and closes encrypted LUKS devices before the script starts")
    argparser.add_argument("-p", type=str, metavar="PASSWORD", help="User password")
    argparser.add_argument("-d", action="store_true", help="Enable commands debug output")
    argparser.add_argument("--version", action="store_true", help="Show version and exit")
    op = argparser.parse_args()

    # optional actions

    # set password before one needs it
    if op.p:
        SETENV["UPASS"] = op.p

    if op.d:
        Spawned.enable_debug_commands()

    if op.version:
        print(Path(__file__).parent.joinpath('VERSION').read_text().strip())
        exit(0)

    if op.hard:
        hard_cleanup()

    clear_installation_cache()

    # main actions
    disk = Disk(select_target_disk())

    # edit partitioning configuration according to your needs
    p1 = StandardPV(1, '/boot/efi').new("100M", VType.EFI).on(disk).reformat()
    p2 = LuksPV(2).new().on(disk)
    lvm_vg = LvmOnLuksVG('vg', 'cryptlvm').new().on(p2)
    root = LvmLV('root', '/').new("15G").on(lvm_vg).reformat('ext4')
    swap = LvmLV('swap', 'swap').new("1G", VType.SWAP).on(lvm_vg)
    home = LvmLV('home', '/home').new("100%FREE").on(lvm_vg).reformat('ext4')

    scheme = Scheme([p1, p2, lvm_vg, root, swap, home])

    partitioner = Partitioner(scheme)
    partitioner.prepare_partitions()

    # wait for Partman and cheat it
    PartmanCheater(scheme).run()

    run_os_installation()

    pi = PostInstaller(scheme)


if __name__ == '__main__':
    run()
