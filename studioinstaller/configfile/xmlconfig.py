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

from xml.etree import ElementTree

from spawned.spawned.spawned import Spawned

from .configfilebase import ConfigFileBase

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

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
