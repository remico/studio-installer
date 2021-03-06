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

from xml.etree import ElementTree

from spawned import Spawned

from .configfilebase import ConfigFileBase

__all__ = ['XmlConfig']


class XmlConfig(ConfigFileBase):
    def __init__(self, filepath, chroot_context=None):
        super().__init__(filepath, chroot_context)
        self.tree = ElementTree.parse(self.abs_filepath)

    def replace(self, re_old: str, str_new: str):
        raise NotImplementedError(f"{__class__.__name__}.replace() method is not implemented")

    def append(self, str_new: str):
        raise NotImplementedError(f"{__class__.__name__}.append() method is not implemented")

    def get_element(self, tag, name):
        for t in self.tree.iter(tag):
            if t.get("name") == name:
                return t

    def insert(self, parent_element, tag, content="", **attributes):
        child = ElementTree.Element(tag)
        child.text = content
        for key, val in attributes.items():
            child.set(key, val)
        parent_element.append(child)
        return child

    def save(self):
        tmpfile = Spawned.tmp_file_path()
        self.tree.write(tmpfile)
        self._execute(f"mv {tmpfile} {self.abs_filepath}")
