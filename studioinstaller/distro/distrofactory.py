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

from .manjaro.manjarodistrofactory import ManjaroDistroFactory
from .ubuntu.ubuntudistrofactory import UbuntuDistroFactory

from ..util.system import distro_name

__all__ = ['DistroFactory']


class DistroFactory:

    __ubuntu = UbuntuDistroFactory()
    __manjaro = ManjaroDistroFactory()

    @staticmethod
    def instance():
        distro = distro_name().lower()

        if "ubuntu" in distro:
            return DistroFactory.__ubuntu
        elif "manjaro" in distro:
            return DistroFactory.__manjaro

        raise NotImplementedError(f"DistroFactory for '{distro}' is not supported")
