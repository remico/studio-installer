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

import requests
import string
from os import getenv
from pathlib import Path
from requests.auth import HTTPBasicAuth

from simplepypipagebuilder import *


api_server = getenv('GITHUB_API_URL')
repo_server = getenv('GITHUB_SERVER_URL')
repo = getenv('REPO')  # owner/repo pair
repo_owner = repo.split('/')[0]
repo_name = repo.split('/')[1]
repo_pass = getenv('PYPI_PASS')


if Path(f"pypi/{repo_name}/index.html").exists():
    pkg_name = repo_name
else:
    pkg_name = getenv('PKG_NAME')


tpl_release = string.Template(f"""\
<a href="git+https://github.com/remico/{repo_name}.git@$version#egg={pkg_name}-$version" data-requires-python="&gt;=3.8">{repo_name}-$version</a>
""")


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


s = requests.Session()

# get repo owner's email
api_url = f"{api_server}/users/{repo_owner}"
user_json = s.get(api_url, auth=HTTPBasicAuth(repo_owner, repo_pass)).json()
set_output_env("REPO_OWNER_EMAIL", user_json['email'])

# get releases in json format using REST API
api_url = f"{api_server}/repos/{repo}/releases"
releases_json = s.get(api_url).json()

# find release versions
releases = [release['tag_name'] for release in releases_json]
print("\nFound releases:")
print(releases)

# # create index file
# release_entries = [tpl_release.substitute(version=release) for release in releases]
# releases_block = ''.join(release_entries).strip()
# tpl_page = string.Template("")
# html_page = tpl_page.substitute(releases=releases_block)
# write_pypi_index_page(pkg_name, html_page)

# another index file builder
source_index_page = read_pypi_index_page(pkg_name)
page_builder = SimplePyPIPageBuilder()
result_index_page = page_builder.build(pkg_name, source_index_page)
write_pypi_index_page(pkg_name, result_index_page)

print("GITHUB_REF:", getenv('GITHUB_REF'))
set_output("READY_TO_PUSH", 1)
