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

"""Parse command line arguments"""

import argparse
from sys import argv as sys_argv

from .util import system

__all__ = ['ArgParser', 'SUBCMD_DEFAULT', 'SUBCMD_SCHEME']

SUBCMD_DEFAULT = "default"
SUBCMD_SCHEME = "scheme"


class ArgParser:
    def __init__(self, prog_name):
        self.argparser = argparse.ArgumentParser(prog=prog_name)
        self.subcmd_registrar = self.argparser.add_subparsers(dest="sub_cmd",
                                                              description="A set of commands for extra functionality")
        self.subcmd_parsers = {}

        argparser = self.argparser

        # MAIN options
        argparser.add_argument("--hard", action="store_true",
                               help="Deactivates LVM volumes and target swap, unmounts target filesystems"
                                    " and closes encrypted LUKS devices before the script starts")
        argparser.add_argument("-p", type=str, metavar="PASSWORD", help="User password")
        argparser.add_argument("-d", action="store_true", help="Enable commands debug output")
        argparser.add_argument("--version", action="store_true", help="Show version and exit")
        argparser.add_argument("--selftest", action="store_true", help="Check environment and own resources and exit")

        DEFAULT_SYSTEM_LABEL = "studio"
        argparser.add_argument("-L", type=str, default=DEFAULT_SYSTEM_LABEL, metavar="SYSTEM_LABEL", help="System label")

        if "ubuntu" in system.distro_name().lower():
            DEFAULT_CHROOT = "/target"
        else:
            DEFAULT_CHROOT = "/mnt"

        argparser.add_argument("--chroot", type=str, default=DEFAULT_CHROOT,
                               help=f"Target system's mountpoint (Default: {DEFAULT_CHROOT})")

        # SUB-COMMANDS
        # default
        default_argparser = self.add_subcommand_parser(SUBCMD_DEFAULT,
            help_msg="Default command, it is implied if no other commands specified")

        default_argparser.add_argument("-n", action="store_true",
            help="Skip disk partitioning and OS installation steps")
        default_argparser.add_argument("-N", action="store_true",
            help="Skip post-installer steps")
        default_argparser.add_argument("--inject", choices=['extra', 'devel'],
            help="Install the tool into the target OS, so that it will be available on the user's first GUI login")

        # scheme-related steps (mount/umount, etc)
        scheme_argparser = self.add_subcommand_parser(SUBCMD_SCHEME,
                                                      help_msg="Actions on the partitioning scheme")

        mount_opts = scheme_argparser.add_mutually_exclusive_group(required=True)
        mount_opts.add_argument("--mount", type=str, const=DEFAULT_CHROOT, metavar="ROOT", nargs='?',
                                help=f"Mount the whole partitioning scheme and exit (Default ROOT: {DEFAULT_CHROOT})")
        mount_opts.add_argument("--umount", action="store_true", help="Unmount the whole partitioning scheme and exit")

    def add_subcommand_parser(self, cmd_name, handler=None, help_msg=""):
        subcmd_parser = self.subcmd_registrar.add_parser(cmd_name, help=help_msg)
        self.subcmd_parsers[cmd_name] = subcmd_parser
        if handler:
            self.set_subcommand_handler(cmd_name, handler)
        return subcmd_parser

    def set_subcommand_handler(self, cmd_name, handler):
        self.subcmd_parsers[cmd_name].set_defaults(func=handler)

    def parse(self):
        """Implements "default" sub-command so that it can be omitted and will be passed implicitly"""

        # first try to parse only known args (to avoid parsing errors)
        parsing_result = self.argparser.parse_known_args()
        ns = parsing_result[0]
        unknown_args = parsing_result[1]

        # if no sub-command specified => default one must be used
        if ns.sub_cmd is None:
            all_args = sys_argv[1:]  # omit the script name itself
            for arg in unknown_args:
                all_args.remove(arg)
            unknown_args.insert(0, SUBCMD_DEFAULT)  # cheat the parser by supplying the default command keyword
            all_args.extend(unknown_args)
            ns = self.argparser.parse_args(all_args)
        else:
            ns = self.argparser.parse_args()  # fallback: check arg list for errors

        return ns  # Namespace
