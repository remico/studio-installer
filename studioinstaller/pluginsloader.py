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

"""Find and load plugins using entry_points mechanism"""

from importlib.metadata import entry_points

from spawned import logger

from . import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PluginsLoader']

ENTRY_POINT_GROUP_PLUGINS = "studioinstaller.plugins"

_p = util.tagged_printer(f'[{__name__}]')


class PluginsLoader:
    def __init__(self):
        all_ep_groups = entry_points()
        if ep_group_plugins := all_ep_groups.get(ENTRY_POINT_GROUP_PLUGINS):
            self.plugins = {ep.name: ep.value for ep in ep_group_plugins}
            _p(f"Installed plugins: {self.list()}")

    def list(self):
        return self.plugins.keys()

    def load(self, name):
        try:
            return self.plugins[name].load()
        except AttributeError:
            _p(logger.fail_s(f"No plugins installed"))
        except KeyError:
            _p(logger.fail_s(f"No plugin '{name}' currently installed"))
