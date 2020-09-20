# Ubuntu Studio Installer
Let's automate boring Ubuntu Studio Linux installation process.

###### DISCLAIMER
> :pushpin: **The tool has limitations and doesn't handle many corner cases**

> :warning: Current implementation will remove EVERYTHING on the disk drive you select!
>
> This is intentional behavior: the tool will use the whole drive space for the new OS.

> :warning: Under a live CD session the tool will get superuser privileges without any password confirmation.
> If something goes wrong, it can damage all data on your HDD/SSD. Use the tool at your own risk.
```
When you run the tool, it will ask you for the target device (e.g. /dev/sda). 
After you specify any valid device and press Enter, the whole device will be cleared, the partition table
will be rewritten, new partitions will be created and formatted according to the defined configuration.
```  

## About
- This is a console tool
- All partitioning requirements can be defined in the partitioning scheme
- Automatic answers for most of the questions during the installation process can be defined in the preseeding file

:information_source: Initially the tool is intended for Ubuntu Studio distro, but in fact, it can also be used
with other Ubuntu-like distros as long as they use `ubiquity` and `partman`.

:information_source: Tested distros:
- Ubuntu Studio 20.04

**The tool can help to automate some routine work one usually does during Ubuntu OS installation:**
- create new partitions (it supports LVM)
- encrypt, mount, unmount, format them
- install OS according to the preconfigured partitioning scheme
- automate some post-installation actions (e.g. install a bootloader, update configuration files, etc)

**Limitations:**
- the partitioning algorithm does NOT support pre-existing partitions yet
- the whole disk drive (user selected) gets cleared even if the new partitions require less space
- entered passwords are visible in the log if logging is enabled (default)
- only fully encrypted installation (including /boot partition) is tested so far

:pushpin: **See [Wiki](../../wiki) for details of:**
- how to configure partitions and edit the preseeding file
- the tool internals

## Requirements
- Ubuntu-like OS (usually, a running Live CD session of the distro you're going to install)
- python >= 3.8
- latest version of `pexpect`
- [`spawned`](https://github.com/remico/spawned) (actually integrated as a submodule)

## Getting the tool
```
$ sudo apt install git python3-pip  # install git and pip3
$ pip3 install --extra-index-url=https://remico.github.io/pypi studioinstaller  # install the tool
$ . ~/.profile  # update $PATH for current shell
```

## Running the tool
- `python3 -m studioinstaller`
- or just `studioinstaller`

### How to use
- boot an Ubuntu Live CD
- get the tool
- edit the partitioning scheme and the `.seed` file according to your needs
- run the tool (use `--help` to see available options)
- specify the target disk device (_last chance to think of backing up your data_) and press Enter
- answer some questions depending on your configuration and OS distribution
> :information_source: during the tool is creating new partitions, popup messages might appear asking you
> to mount and/or decrypt the newly created volumes. Just ignore/close these popups.
>
> :information_source: if the partitions get mounted somehow, installer will eventually propose you
>to unmount them. Just agree.
