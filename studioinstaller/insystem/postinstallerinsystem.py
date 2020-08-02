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

"""Performs in-system post-installation action if scheduled"""

from spawned import SpawnedSU, ENV

from studioinstaller import util
from ..configfile import IniConfig

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['PostInstallerInsystem']


class PostInstallerInsystem:
    def run(self):
        install_software()
        setup_keyboard()

        # unschedule studioinstaller_extra
        config = IniConfig(f"{ENV('HOME')}/.profile")
        config.replace(r"studioinstaller .*", "")


def install_software():
    SpawnedSU.do("""
        apt -q install -y \
        okular okular-extra-backends kate kwrite \
        vim build-essential git-gui gitk kdiff3 kompare doxygen graphviz doxyqml python3-pip \
        krusader \
        pavucontrol dconf-editor apt-file ethtool nmap p7zip-full unrar-free xterm net-tools htop tilix \
        > /dev/null

        # apt -q install -y ttf-mscorefonts-installer  > /dev/null
        # apt -q install -y chromium-browser  > /dev/null
        # apt -q install -y pepperflashplugin-nonfree  > /dev/null
        """)


def setup_keyboard():
    # TODO also check /etc/default/keyboard
    if home := ENV('HOME'):
        util.deploy_resource("keyboard-layout.xml",
                             f"{home}/.config/xfce4/xfconf/xfce-perchannel-xml/")
