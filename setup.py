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

import setuptools
from importlib import resources
from pathlib import Path

__author__ = "Roman Gladyshev"
__email__ = "remicollab@gmail.com"
__copyright__ = "Copyright (c) 2020, REMICO"
__license__ = "MIT"


with open("README.md") as f:
    long_description = f.read()


def version():
    return resources.read_text('studioinstaller', 'VERSION')


def data_files():
    files = [str(f) for f in Path("preseed").glob("*") if f.is_file()]
    return [('studioinstaller-data', files)]


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
    name="studioinstaller",
    version=version(),
    author="remico",
    author_email="remicollab@gmail.com",
    description="A console tool for Ubuntu Studio OS installation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remico/studio-installer",
    project_urls={
        "Source Code": "https://github.com/remico/studio-installer",
        "Documentation": "https://github.com/remico/studio-installer/wiki"
    },
    packages=setuptools.find_packages(exclude=['sndbx', 'test', 'tests']),
    package_data={'': ['VERSION']},
    data_files=data_files(),
    # py_modules=[],
    # register executable <command>=<pkg><module>:<attr>
    entry_points={
        'console_scripts': ['studioinstaller=studioinstaller.main:run']
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.8',
    install_requires=[
        'pexpect',
        'pyyaml',
        # 'spawned @ git+https://github.com/remico/spawned.git@master'  # integrated as a submodule
    ],
    license='MIT',
    platforms=['POSIX'],
    cmdclass={'bdist_wheel': bdist_wheel},
)
