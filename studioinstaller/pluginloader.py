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

"""Find and load plugins using entry_points mechanism"""

from importlib.metadata import entry_points
from . import util

__all__ = ['PluginLoader']

ENTRY_POINT_GROUP_PLUGINS = "studioinstaller.plugins"

# plugin descriptor attributes
D_ATTR_NAME = "name"
D_ATTR_API = "api"
D_ATTR_HELP_MSG = "help"
D_ATTR_MAIN_ENTRY = "main_entry"
D_ATTR_OPTS = "options"

_tlog = util.tagged_logger(f'[{__name__}]')


def _attr(plugin_descriptor, attr_name, default=None):
    return getattr(plugin_descriptor, attr_name, default)


class PluginLoader:
    def __init__(self, api):
        all_ep_groups = entry_points()

        self.api_major = int(api.split('.')[0])
        self._plugins = {}

        if eps_plugins := all_ep_groups.get(ENTRY_POINT_GROUP_PLUGINS):
            # key - plugin_descriptor.name attribute
            # value - plugin_descriptor module itself (already loaded)
            all_plugins = {getattr(d := ep.load(), D_ATTR_NAME): d for ep in eps_plugins}

            # validate api compatibility
            for name, plugin in all_plugins.items():
                plugin_api = _attr(plugin, D_ATTR_API)
                plugin_api_major = int(plugin_api.split('.')[0])
                if self.api_major == plugin_api_major:
                    self._plugins[name] = plugin

        _tlog("Found plugins:", self.names())

    def names(self):
        return list(self.plugins.keys())

    def descriptors(self):
        return list(self.plugins.values())

    @property
    def plugins(self):
        return self._plugins

    def plugin_entry_point(self, name):
        d = self.plugins.get(name)
        return _attr(d, D_ATTR_MAIN_ENTRY)

    def plugin_help_message(self, name):
        d = self.plugins.get(name)
        return _attr(d, D_ATTR_HELP_MSG)

    def plugin_options(self, name):
        d = self.plugins.get(name)
        return _attr(d, D_ATTR_OPTS)

    # def run_plugin_action(self, name, **kwargs):
    #     plugin_action = self.load(name)
    #     if plugin_action:
    #         plugin_action(**kwargs)

