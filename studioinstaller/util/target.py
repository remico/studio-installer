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

from importlib.metadata import files as app_files
from pathlib import Path

from spawned import Spawned, SpawnedSU, logger, ask_user, ENV, SETENV

from .system import owner_uid
from .util import tagged_printer, package_name

__all__ = [
    'resource_file',
    'preseeding_file',
    'get_target_upass',
    'read_upass_from_preseeding_file',
    'target_user',
    'target_home',
    'ready_for_postinstall',
    'deploy_resource',
]

_tp = tagged_printer("[target]")


def resource_file(filename):
    """Returns the first available file with matching name"""
    package = package_name()
    if l := [f for f in app_files(package) if str(f).endswith(filename)]:
        return str(l[0].locate())
    return ""


def preseeding_file():
    """Returns the first available .seed file"""
    # TODO move .seed file inside the package and use resource API
    package = package_name()
    if l := [f for f in app_files(package) if str(f).endswith('.seed')]:
        return str(l[0].locate())
    return ""


def get_target_upass(insystem_scheduled):
    if tupass := ENV('TUPASS'):
        return tupass

    tupass = read_upass_from_preseeding_file("user-password")

    if not tupass and not insystem_scheduled:
        tupass = read_upass_from_preseeding_file("user-password-crypted")

    if not tupass:
        tupass = ask_user("Enter user password for target system:")

    SETENV('TUPASS', tupass)
    return tupass


def read_upass_from_preseeding_file(pass_key):
    prefile = preseeding_file()
    if not prefile:
        return ""

    template = f"grep 'passwd/%s' {prefile} | grep -vP '#' | cut -d' ' -f4"
    return Spawned.do(template % pass_key)


def target_user(root_fs: str):
    return Spawned.do(f'ls {root_fs}/home/ | grep -v "lost+found"')


def target_home(root_fs: str):
    return f"{root_fs}/home/{user}" if (user := target_user(root_fs)) else ""


def ready_for_postinstall(chroot):
    """True if the chroot path exists and nothing mounted inside, False otherwise"""
    path = Path(chroot)
    return path.exists() and not any(path.iterdir())


def deploy_resource(filename, dst_path, owner=None, mode=None):
    src_path = resource_file(filename)
    dst_full_path = dst_path if dst_path.endswith(filename) else f"{dst_path}/{filename}"

    if not Path(dst_full_path).parent.exists():
        colored_warn = logger.fail_s("WARNING:")
        _tp(f"{colored_warn} Path {Path(dst_full_path).parent} doesn't exist; deploy_resource('{filename}') skipped")
        return  # just skip processing for now

    owner = owner or owner_uid(Path(dst_full_path).parent)
    mode = mode or 0o664

    SpawnedSU.do(f"""
        cp {src_path} {dst_path}
        chown {owner}:{owner} {dst_full_path}
        chmod {mode} {dst_full_path}
        """)
