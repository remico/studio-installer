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

import yaml
from pathlib import Path

from spawned import SpawnedSU, Spawned, ENV

from ..configfile import XmlConfig
from .. import util

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"

__all__ = ['InsystemInstaller']

_tp = util.tagged_printer("Insystem")

TPL_CMD_APT_INSTALL = "apt -q install -y %s > /dev/null"
HOME = ENV('HOME')
USER = ENV('USER')


class InsystemInstaller:
    def run(self):
        install_software()
        setup_keyboard()
        setup_mouse()
        deploy_repo_bin()


def install_software():
    SpawnedSU.do_script("""
        apt -q update > /dev/null

        apt -q install -y \
        okular okular-extra-backends kate kwrite \
        vim build-essential git-gui gitk kdiff3 kompare doxygen graphviz doxyqml python3-pip \
        krusader \
        pavucontrol dconf-editor apt-file ethtool nmap p7zip-full unrar-free xterm net-tools htop tilix \
        > /dev/null

        # apt -q install -y ttf-mscorefonts-installer  > /dev/null
        # apt -q install -y chromium-browser  > /dev/null
        # apt -q install -y pepperflashplugin-nonfree  > /dev/null
        """, bg=False)


def setup_keyboard():
    # TODO also check /etc/default/keyboard

    tgt_path = f"{HOME}/.config/xfce4/xfconf/xfce-perchannel-xml"

    if Path(tgt_path).exists():
        # deploy keyboard config
        util.deploy_resource("keyboard-layout.xml", tgt_path)

        # setup keyboard layouts panel
        file = XmlConfig(f"{tgt_path}/xfce4-panel.xml")
        parent = file.get_element("property", "plugin-ids")
        file.insert(parent, "value", type="int", value="14")
        parent = file.get_element("property", "plugins")
        parent = file.insert(parent, "property", name="plugin-14", type="string", value="xkb")
        file.insert(parent, "property", name="display-type", type="uint", value="1")
        file.insert(parent, "property", name="display-name", type="uint", value="1")
        file.insert(parent, "property", name="group-policy", type="uint", value="1")
        file.insert(parent, "property", name="display-scale", type="uint", value="82")
        file.insert(parent, "property", name="display-tooltip-icon", type="bool", value="false")
        file.save()


def setup_mouse():
    # find the settings in ~/.config/xfce4/xfconf/xfce-perchannel-xml/pointers.xml
    if Path(f"{HOME}/.config/xfce4").exists():
        Spawned.do_script("xfce4-mouse-settings", bg=False)


def deploy_repo_bin():
    yapath = util.resource_file("config.yaml")
    if not yapath:
        return

    with open(yapath) as yafile:
        try:
            yaopts = yaml.safe_load(yafile)
        except yaml.YAMLError as e:
            _tp(str(e))
            return

    url_ssh = yaopts['url_ssh_dir']
    repo_bin = yaopts['git_repo_bin']

    # setup ssh key
    Spawned.do_script(f"""
        wget -P {HOME}/.ssh --user={repo_bin['user']} --password={repo_bin['pass']} \
            {url_ssh}/id_rsa \
            {url_ssh}/known_hosts
        chmod 600 {HOME}/.ssh/id_rsa
        chmod 644 {HOME}/.ssh/known_hosts
        """, bg=False)

    # clone repo, deploy stuff
    Spawned.do_script(f"""
        cd {HOME} &&
        rm -rf {HOME}/bin &&
        echo "Cloning 'bin' repo..." &&
        git clone --recurse-submodules {repo_bin['path']} &&
        rm -rf {HOME}/.ssh &&
        echo "Deploing 'bin' repo..." &&
        {HOME}/bin/setup/setup_homedir.sh
        """, bg=False)
