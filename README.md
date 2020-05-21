# Linux Studio Installer
Let's automate boring Linux installation process

###### DISCLAIMER
> :pushpin: **The tool has limitations and doesn't handle many corner cases**

> :warning: Under a live CD session the tool will run with superuser privileges without any password confirmation.
> If something goes wrong, it can damage all data on your HDD. YOU HAS BEEN WARNED.

## About
This is a console tool aimed to (semi-)automate installation of Ubuntu/Manjaro Linux.

**The tool can help to automate some routine work one usually does during OS installation:**
- create new partitions
- encrypt, mount, unmount, format them
- install an OS according to the preconfigured partitioning scheme
- automate some post-installation actions (e.g. install a bootloader, update configuration files, etc)

**The tool has a lot of limitations, e.g.:**
- partitioning algorithm doesn't support existing partitions yet, new partitions need to be created
- ext* and btrfs FS are supported only
- many parameters/options are hardcoded
- entered passwords are visible in the logs
- only very basic installation scenarios have been tested so far


## Requirements
- Ubuntu/Manjaro Linux
- python >= 3.8
- pip
- git

## Getting the tool
```
$ pip3 install --extra-index-url=https://remico.github.io/pypi studioinstaller
```

## Running the tool
`$ studioinstaller`

### How to use
- boot a Live CD session
- get the tool
- edit the partitioning scheme and the `.seed` file (for Ubuntu) according to your needs
- run the tool (use `--help` to see available options)
- specify the target disk device (_the last chance to think of backing up your data_) and press Enter
- answer some questions depending on your configuration and OS distribution
> :information_source: after the tool creates new partitions, popup messages might appear asking you
> to mount and/or decrypt the newly created volumes. Just ignore/close such popups.
>
> :information_source: if the partitions get mounted somehow, installer will eventually propose you
>to unmount them, just accept.
