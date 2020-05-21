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

import platform
import setuptools
from pathlib import Path


if 'linux' not in platform.system().lower():
    raise OSError('The package requires GNU Linux. Aborting installation...')


def data_files():
    return [
        ('studioinstaller-data', [str(f) for f in Path("preseed").glob("*") if f.is_file()]),
        ('studioinstaller-data/calamares', [str(f) for f in Path("preseed/calamares").glob("*") if f.is_file()])
    ]


# make the distribution platform dependent
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
            # self.plat_name_supplied = True
            # self.plat_name = "manylinux1_x86_64"
except ImportError:
    bdist_wheel = None


setuptools.setup(
    data_files=data_files(),
    cmdclass={
        'bdist_wheel': bdist_wheel
    }
)
