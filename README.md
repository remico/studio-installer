# studio-installer
Let's automate boring Ubuntu Studio Linux installation process.

###### DISCLAIMER
> :pushpin: **The tool is under development and can't be used by enduser at the moment**

> :warning: Current implementation will remove EVERYTHING on the disk you select!
>
> This is intentional behavior: the tool will use the whole disk space for the new OS.

> :warning: Under a live CD session the tool will get superuser privileges without any password confirmation.
> If something goes wrong, it can damage all data on your HDD, SSD, etc. Use the tool at your own risk.  
```
When you run the tool, it will ask you for the target device (e.g. /dev/sda). 
After you specify any valid device and press Enter, the whole device will be cleared, the partition table
will be rewritten, new partitions will be created and formatted according to the defined configuration.
```  

>:information_source: The tool can be used with other Ubuntu-like distro installers
> provided they use `ubiquity` and `partman`.

### How it works
It's a console tool.
All partitioning requirements can be defined in the partitioning scheme.
Automatic answers for most of the questions during the installation process can be defined in the preseeding file. 

The tool's working cycle consists of several stages:
- Prepare partitions:
  - process a defined partitioning scheme
  - cleanup space
  - create partitions
  - [optionally] encrypt and format partitions, setup LVM
- Depending on the partitioning scheme, run background bash scripts instructing `partman` how to deal with the partitions
- Set pre-configured values from the preseeding file
- Run the OS installer (`ubiquity` at the moment)
- Run post-installation actions:
  - configure encryption and LVM systems (if there are any LUKS and/or LVM devices in the system)
  - rebuild initrd
  - configure and install bootloader
  - some extra actions, e.g. install additional packages, setup user settings, etc 

:pushpin: See [Wiki](../../wiki/Home) to know how to configure partitions and edit the preseeding file.

### Requirements
- python >= 3.8 (on Ubuntu 20.04 live CD works out of the box)
- latest version of `pexpect`
- [`spawned`](https://github.com/remico/spawned) (actually integrated as a submodule)

### Getting the tool
```
$ sudo apt install git python3-pip  # install git and pip3
$ [sudo] pip3 install git+https://github.com/remico/studio-installer.git  # install the tool
```

### Running the tool
- `python3 -m studioinstaller`
- or just `studioinstaller` if it was installed with `sudo`

### How to use
- boot an Ubuntu Live CD
- get the tool
- edit the partitioning scheme and the `.seed` file according to your needs
- run the tool (use `--help` to see available options)
- specify the target disk device (_last chance to backup your data_) and press Enter
- answer some questions depending on your configuration and OS distribution
