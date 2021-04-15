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

from itertools import starmap
from functools import partial
from html import escape
from html.parser import HTMLParser
from os import getenv
from pathlib import Path

__all__ = [
    'read_pypi_index_page',
    'write_pypi_index_page',
    'SimplePyPIPageBuilder',
    ]


def read_pypi_index_page(packagename):
    # {repo}/pypi/{packagename}/index.html
    return Path(f"pypi/{packagename}/index.html").read_text()


def write_pypi_index_page(packagename, html):
    # {repo}/pypi/{packagename}/index.html
    Path(f"pypi/{packagename}/index.html").write_text(html)


def version(packagename):
    # {repo}/{packagename}/VERSION
    return Path(packagename, "VERSION").read_text().strip()


def _update_version(packagename, tag, attr_name, attr_val):
    # GITHUB_REF is refs/heads/{branch|tag}
    # GITHUB_SHA is the commit's SHA value
    branch = getenv('GITHUB_REF', "").split('/')[-1]

    if tag == 'a' and f"@{branch}" in attr_val:
        end = attr_val.rfind('-')
        # return f'{attr_name}="{attr_val[:end]}-$version"'
        return f'{attr_name}="{attr_val[:end]}-{version(packagename)}"'
    else:
        return f'{attr_name}="{escape(attr_val)}"'


class SimplePyPIPageBuilder(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.packagename = ""
        self.output = ""

    def handle_decl(self, decl: str) -> None:
        self.output += f"<!{decl}>"

    def handle_starttag(self, tag: str, attrs) -> None:
        # prevent useless execution
        if not self.packagename:
            raise ValueError("Package name isn't set")

        mapper = partial(_update_version, self.packagename, tag)
        attrs_formatted = starmap(mapper, attrs)

        attrs_single_string = ' '.join(attrs_formatted)
        if attrs_single_string:
            attrs_single_string = ' ' + attrs_single_string

        self.output += f"<{tag}{attrs_single_string}>"

    def handle_data(self, data: str) -> None:
        self.output += data

    def handle_endtag(self, tag: str) -> None:
        self.output += f"</{tag}>"

    def build(self, packagename: str, source_html: str) -> str:
        self.packagename = packagename
        self.output = ""
        self.feed(source_html)
        return self.output


if __name__ == '__main__':
    # unit testing
    p = SimplePyPIPageBuilder()
    package = "studioinstaller"
    page = read_pypi_index_page(package)
    r = p.build(package, page)
    print(r)
