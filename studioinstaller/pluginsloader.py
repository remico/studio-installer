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

from .argparser import *
from . import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PluginsLoader']

ENTRY_POINT_GROUP_PLUGINS = "studioinstaller.plugins"

# plugin descriptor attributes
D_ATTR_NAME = "name"
D_ATTR_HELP_MSG = "help"
D_ATTR_MAIN_ENTRY = "main_entry"
D_ATTR_OPTS = "options"

_p = util.tagged_printer(f'[{__name__}]')


def _attr(plugin_descriptor, attr_name, default=None):
    return getattr(plugin_descriptor, attr_name, default)


class PluginsLoader:
    def __init__(self):
        all_ep_groups = entry_points()

        self.plugin_descriptors = {}
        self.plugins = {}

        if eps_plugins := all_ep_groups.get(ENTRY_POINT_GROUP_PLUGINS):
            # key - plugin_descriptor.name attribute
            # value - plugin_descriptor module itself (already loaded)
            self.plugins = {getattr(d := ep.load(), D_ATTR_NAME): d for ep in eps_plugins}
        _p(f"Found plugins: {self.list()}")

    def list(self):
        return self.plugins.keys()

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
                _p(logger.warning_s(f"Skipping plugin '{plugin_name}': plugin's main_entry is not defined"))

    def run_plugin_action(self, name, **kwargs):
        plugin_action = self.load(name)
        if plugin_action:
            plugin_action(**kwargs)

