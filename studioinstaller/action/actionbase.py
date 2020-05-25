#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Abstract action interface """

__author__ = 'remico <remicollab@gmail.com>'

from abc import ABC, abstractmethod

__all__ = ['ActionBase']


class ActionBase(ABC):
    @abstractmethod
    def iterator(self, scheme):
        pass

    @abstractmethod
    def serve_disk(self, disk):
        pass

    @abstractmethod
    def serve_standard_pv(self, pt):
        pass

    @abstractmethod
    def serve_luks_pv(self, pt):
        pass

    @abstractmethod
    def serve_lvm_on_luks_vg(self, pt):
        pass

    @abstractmethod
    def serve_lvm_lv(self, pt):
        pass
