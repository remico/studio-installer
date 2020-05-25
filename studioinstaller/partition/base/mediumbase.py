#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Abstract base medium """

__author__ = 'remico <remicollab@gmail.com>'

from abc import ABC, abstractmethod
from typing import final

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
        if not self.ready:
            self._a_execute(action)
            self._ready = True

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
