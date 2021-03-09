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

from abc import abstractmethod, ABC

__all__ = ['OsInstaller']

class OsInstaller(ABC):
    def __init__(self, scheme) -> None:
        self.scheme = scheme

    def execute(self):
        self._prepare_installation()
        self._setup_unattended_installation()
        self._begin_installation()

    @abstractmethod
    def _prepare_installation(self):
        pass

    @abstractmethod
    def _setup_unattended_installation(self):
        pass

    @abstractmethod
    def _begin_installation(self):
        pass


