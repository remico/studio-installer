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

from spawned import ask_user, ENV
from .partitionbase import Partition

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['LUKS']


class LUKS(Partition):
    def __init__(self, passphrase=None, **kwargs):
        self._passphrase = passphrase
        super().__init__(**kwargs)

    @property
    def passphrase(self):
        # FIXME remove checking for user
        if not self._passphrase and ENV('USER') != 'user':
            self._passphrase = ask_user("Enter LUKS passphrase:")
        return self._passphrase

    @property
    def luks_url(self):
        # FIXME is this correct for all use cases?
        # return self.url if self.isphysical or (self.islvm and not self.iscontainer) else self.parent.url
        return self.url
