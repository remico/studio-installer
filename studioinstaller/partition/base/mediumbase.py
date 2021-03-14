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

"""Abstract base medium"""

import re
from abc import ABC, abstractmethod

__all__ = ['MediumBase', 'URL_PV', 'URL_DISK', 'URL_MAPPED', 'URL_LVM_LV']


def _cut_trailing_digits(s):
    # cut trailing digits
    return m.group(1) if m := re.match(r"(.*)\d*$", s) else ''


def URL_PV(id_):
    return f"/dev/{id_}"


def URL_MAPPED(id_):
    return f"/dev/mapper/{id_}"


def URL_LVM_LV(vg, lv):
    return f"/dev/{vg}/{lv}"


def URL_DISK(id_):
    return f"/dev/{_cut_trailing_digits(id_)}"


class MediumBase(ABC):
    @abstractmethod
    def __init__(self, id_, **kwargs):
        super().__init__(**kwargs)

        self._parent = None
        self._id = str(id_)

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return f"{self.parent.id}{self._id}" if str(self._id).isdigit() and self.parent else self._id

    @property
    @abstractmethod
    def url(self):
        pass
