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

"""Parse command line arguments"""

import argparse
from sys import argv as sys_argv

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['ArgParser', 'SUBCMD_DEFAULT', 'SUBCMD_SCHEME', 'SUBCMD_INSYSTEM']

SUBCMD_DEFAULT = "default"
SUBCMD_SCHEME = "scheme"
SUBCMD_INSYSTEM = "inplace"


class ArgParser:
    def __init__(self, prog_name):
        self.argparser = argparse.ArgumentParser(prog=prog_name)
        self.subcmd_registrar = self.argparser.add_subparsers(dest="sub_cmd",
                                                              description="Set of commands for extra functionality")
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

        DEFAULT_CHROOT = "/target"
        argparser.add_argument("--chroot", type=str, default=DEFAULT_CHROOT,
                               help=f"Target system's mountpoint (Default: {DEFAULT_CHROOT})")

        # SUB-COMMANDS
        # default
        default_argparser = self.add_subcommand_parser(SUBCMD_DEFAULT,
            help_msg="Default command, it is implied if no other commands specified")

        default_argparser.add_argument("-n", action="store_true",
            help="Skip disk partitioning and OS installation steps, run default post-install steps only")
        default_argparser.add_argument("--post", action="store_true",
            help="Schedule extra post-install steps which will be performed on user's first GUI login")

        # scheme-related steps (mount/umount, etc)
        scheme_argparser = self.add_subcommand_parser(SUBCMD_SCHEME,
                                                      help_msg="Actions on the partitioning scheme")

        mount_opts = scheme_argparser.add_mutually_exclusive_group(required=True)
        mount_opts.add_argument("--mount", type=str, const=DEFAULT_CHROOT, metavar="ROOT", nargs='?',
                                help=f"Mount the whole partitioning scheme and exit (Default ROOT: {DEFAULT_CHROOT})")
        mount_opts.add_argument("--umount", action="store_true", help="Unmount the whole partitioning scheme and exit")

        # extra in-system steps (upon GUI login)
        inplace_argparser = self.add_subcommand_parser(SUBCMD_INSYSTEM,
                                                       help_msg="Run extra post-install steps only")

    def add_subcommand_parser(self, cmd_name, handler=None, help_msg=""):
        subcmd_parser = self.subcmd_registrar.add_parser(cmd_name, help=help_msg)
        self.subcmd_parsers[cmd_name] = subcmd_parser
        if handler:
            self.set_subcommand_handler(cmd_name, handler)
        return subcmd_parser

    def set_subcommand_handler(self, cmd_name, handler):
        self.subcmd_parsers[cmd_name].set_defaults(func=handler)

    def parse(self):
        """Implement "default" sub-command (it can be omitted and will be passed implicitly)"""

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
