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

"""Partitions hierarchy"""

from .base import Container

__all__ = ['VGLvmOnLuks']


class VGLvmOnLuks(Container):
    def __init__(self, vg, id_, **kwargs):
        super().__init__(id_=id_, vg=vg, **kwargs)

    def _a_execute(self, action):
        action.serve_lvm_on_luks_vg(self)

    def on(self, parent):
        # magic attribute, used in LUKS
        parent._evaluated_mapper_id = self.mapperID  # warning: magic attribute
        return super().on(parent)
