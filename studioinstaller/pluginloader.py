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

from spawned import logger

from .argparser import *
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
        self.plugin_descriptors = {}
        self.plugins = {}

        if eps_plugins := all_ep_groups.get(ENTRY_POINT_GROUP_PLUGINS):
            # key - plugin_descriptor.name attribute
            # value - plugin_descriptor module itself (already loaded)
            all_plugins = {getattr(d := ep.load(), D_ATTR_NAME): d for ep in eps_plugins}

            # validate api compatibility
            for name, plugin in all_plugins.items():
                plugin_api = _attr(plugin, D_ATTR_API)
                plugin_api_major = int(plugin_api.split('.')[0])
                if self.api_major == plugin_api_major:
                    self.plugins[name] = plugin

        _tlog("Found plugins:", self.list())

    def list(self):
        return list(self.plugins.keys())

    def extend_argparser(self, argparser):
        for plugin_name in self.list():
            d = self.plugins[plugin_name]  # plugin descriptor
            main_entry = _attr(d, D_ATTR_MAIN_ENTRY)

            if main_entry:
                subcmd_parser = argparser.add_subcommand_parser(plugin_name, main_entry,
                                                                help_msg=_attr(d, D_ATTR_HELP_MSG))
                plugin_opts = _attr(d, D_ATTR_OPTS)
                for opt_name, opt_params in plugin_opts.items():
                    subcmd_parser.add_argument(opt_name, **opt_params)
            else:
                _tlog(logger.warning_s(f"Skipping plugin '{plugin_name}': plugin's main_entry is not defined"))

    def run_plugin_action(self, name, **kwargs):
        plugin_action = self.load(name)
        if plugin_action:
            plugin_action(**kwargs)

