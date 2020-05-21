import setuptools
from pkg_resources import resource_string


with open("README.md") as f:
    long_description = f.read()


def version():
    return resource_string('studioinstaller', 'VERSION').decode("utf-8")


def dependency_links():
    pkgs = setuptools.find_packages()
    print("@@ packages:", pkgs)
    return [] if 'spawned' in pkgs else ['git+https://github.com/remico/spawned.git@master']


# make the distribution platform dependent
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
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
    install_requires=['pexpect'],
    dependency_links=dependency_links(),
    license='MIT',
    platforms=['POSIX'],
    cmdclass={'bdist_wheel': bdist_wheel},
)
