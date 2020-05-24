import setuptools
from pkg_resources import resource_string
from pathlib import Path


with open("README.md") as f:
    long_description = f.read()


def version():
    return resource_string('studioinstaller', 'VERSION').decode("utf-8")


def data_files():
    files = [
        'stuff/studioinstaller.seed'
    ]
    return [('studioinstaller-data', [f for f in files if Path(f).exists()])]


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
    description="A semi-automatic Ubuntu Studio OS installer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remico/studio-installer",
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
        # 'spawned @ git+https://github.com/remico/spawned.git@master'  # integrated as a submodule
    ],
    license='MIT',
    platforms=['POSIX'],
    cmdclass={'bdist_wheel': bdist_wheel},
)
