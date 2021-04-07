# Linux Studio Installer
Let's automate boring Linux installation process.

###### DISCLAIMER
> :pushpin: **The tool has limitations and doesn't handle many corner cases**

> :warning: Under a live CD/USB session the tool will run with superuser privileges without any password confirmation.
> If something goes wrong, it can damage all data on your HDD/SSD. YOU HAS BEEN WARNED.

## About
This is a console tool aimed to (semi-)automate installation of Ubuntu/Manjaro Linux.

**The tool can help to automate some routine work one usually does during OS installation:**
- create new partitions
- encrypt, mount, unmount, format them
- install an OS according to the preconfigured partitioning scheme
- automate some post-installation actions (e.g. install a bootloader, update configuration files, etc)

**The tool has a lot of limitations, a few of them are:**
- the partitioning algorithm doesn't support existing partitions yet, new partitions need to be created
- entered passwords are visible in the logs if logging is enabled (default)
- only very basic installation scenarios have been tested so far


## Requirements
- Ubuntu/Manjaro Linux CD/USB
- python >= 3.8

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
- boot a Live CD/USB session
- get the tool
- edit the partitioning scheme and the `.seed` file (for Ubuntu) according to your needs
- run the tool (use `--help` to see available options)
- specify the target disk device (_the last chance to think of backing up your data_) and press Enter
- answer some questions depending on your configuration and OS distribution
> :information_source: during the tool is creating new partitions, popup messages might appear asking you
> to mount and/or decrypt the newly created volumes. Just ignore/close such popups.
>
> :information_source: if the partitions get mounted somehow, installer will eventually propose you
>to unmount them, just accept.
