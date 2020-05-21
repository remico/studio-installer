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
from traceback import format_exc

from spawned import logger

from . import util

__all__ = ['PluginLoader', 'PluginRunner']

packagename = util.package_name()

ENTRY_POINT_GROUP_PLUGINS = f"{packagename}.plugins"
PLUGIN_API = 1

# plugin descriptor attributes
D_ATTR_NAME = "name"
D_ATTR_API = "api"
D_ATTR_HELP_MSG = "help"
D_ATTR_MAIN_ENTRY = "main_entry"
D_ATTR_OPTS = "options"


def _attr(plugin_descriptor, attr_name, default=None):
    return getattr(plugin_descriptor, attr_name, default)


class PluginLoader:
    API = PLUGIN_API

    def __init__(self):
        self._plugins = {}
        all_ep_groups = entry_points()

        if eps_plugins := all_ep_groups.get(ENTRY_POINT_GROUP_PLUGINS):
            # key - plugin_descriptor.name attribute
            # value - plugin_descriptor module itself (already loaded)
            all_plugins = {getattr(d := ep.load(), D_ATTR_NAME): d for ep in eps_plugins}

            # validate api compatibility
            self._plugins = {name: d for name, d in all_plugins.items() if PluginLoader.API == _attr(d, D_ATTR_API)}

        _tlog = util.tagged_logger(f'[{self.__class__.__name__}]')
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


class PluginRunner:
    def __init__(self, name) -> None:
        self.name = name
        self.api = PLUGIN_API

    def set_options(self, opns):
        self.opns = opns

    def __call__(self):
        loader = PluginLoader()
        main_entry = loader.plugin_entry_point(self.name)

        try:
            main_entry(self.api, self.opns)
        except Exception as e:
            _tlog = util.tagged_logger(f'[{self.__class__.__name__}]')
            _tlog(logger.fail_s(f"Plugin '{self.name}': {e}"))
            _tlog(logger.warning_s(format_exc()))
