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

from os import getenv


# usage: ${{ steps.<step-id>.outputs.<key> }}
def set_output(key, val):
    print(f"::set-output name={key}::{val}")


# usage: according to the shell type (e.g. in bash - $KEY)
def set_output_env(key, val):
    with open(getenv('GITHUB_ENV'), "a") as env_file:
        print(f"{key}={val}", file=env_file)


# usage: according to the shell type (e.g. in bash - $KEY)
def set_output_env_multi(key, lines, delimiter='EOF'):
    with open(getenv('GITHUB_ENV'), "a") as env_file:
        print(f"{key}<<{delimiter}\n{lines}\n{delimiter}", file=env_file)
