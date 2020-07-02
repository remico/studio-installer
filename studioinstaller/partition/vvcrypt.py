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

"""Partitions hierarchy"""

from .base import FS

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['VVCrypt']


class VVCrypt(FS):
    def __init__(self, id_, mountpoint=''):
        super().__init__(id_=id_, mountpoint=mountpoint)

    def _a_execute(self, action):
        action.serve_encrypted_vv(self)

    def on(self, parent):
        # magic attribute, used in LUKS
        parent._evaluated_mapper_id = self.mapperID  # warning: magic attribute
        return super().on(parent)