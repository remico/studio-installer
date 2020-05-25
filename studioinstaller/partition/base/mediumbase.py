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

""" Abstract base medium """

from abc import ABC, abstractmethod
from typing import final

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['MediumBase', 'URL_PV', 'URL_DISK', 'URL_MAPPED']


def _cut_digits(s):
    return ''.join(i for i in s if not i.isdigit())


def URL_PV(id_):
    return f"/dev/{id_}"


def URL_MAPPED(id_):
    return f"/dev/mapper/{id_}"


def URL_DISK(id_):
    return f"/dev/{_cut_digits(id_)}"


class MediumBase(ABC):
    @abstractmethod
    def __init__(self, id_, **kwargs):
        super().__init__(**kwargs)

        self._ready = False
        self._parent = None
        self._id = id_

    @final
    def execute(self, action):
        print(f"execute <{action.__class__.__name__}>:", f"<{self.__class__.__name__}>::{self.id}")
        self._a_execute(action)

    @abstractmethod
    def _a_execute(self, action):
        pass

    def on(self, parent):
        self._parent = parent
        return self

    @property
    def parent(self):
        return self._parent

    @property
    def ready(self):
        return self._ready

    @property
    def id(self):
        return f"{self.parent.id}{self._id}" if str(self._id).isdigit() and self.parent else self._id

    @property
    @abstractmethod
    def url(self):
        pass
