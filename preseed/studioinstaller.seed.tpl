# Partman
ubiquity	partman-auto/init_automatically_partition	select	80custom__________custom
ubiquity	partman/confirm	boolean	true
ubiquity	partman/unmount_active	boolean  true

# Locale
casper languagechooser/language-name string English
casper countrychooser/shortlist string US
ubiquity localechooser/supported-locales multiselect en_US.UTF-8
keyboard-configuration keyboard-configuration/layoutcode string us

ubiquity debian-installer/locale string en_US
ubiquity debian-installer/language string en
ubiquity debian-installer/country string US
keyboard-configuration console-setup/ask_detect boolean false
#d-i console-setup/layoutcode string us
keyboard-configuration keyboard-configuration/xkb-keymap multiselect us,ru
#keyboard-configuration keyboard-configuration/variant select English (US)
#keyboard-configuration keyboard-configuration/layout select English (US)

# Method for toggling between national and Latin mode:
# Choices: Caps Lock, Right Alt (AltGr), Right Control, Right Shift, Right Logo key, Menu key, Alt+Shift, Control+Shift, Control+Alt, Alt+Caps Lock, Left Control+Left Shift, Left Alt, Left Control, Left Shift, Left Logo key, Scroll Lock key, No toggling
keyboard-configuration keyboard-configuration/toggle select Super+Space

# Method for temporarily toggling between national and Latin input:
# Choices: No temporary switch, Both Logo keys, Right Alt (AltGr), Right Logo key, Left Alt, Left Logo key
#keyboard-configuration keyboard-configuration/switch select No temporary switch

# Network
d-i netcfg/get_hostname string unassigned-hostname
d-i netcfg/get_domain string unassigned-domain
d-i netcfg/choose_interface select auto

d-i netcfg/link_wait_timeout string 10
d-i netcfg/hostname string asterisk

# Clock
d-i clock-setup/utc-auto boolean true
d-i clock-setup/utc boolean true
d-i time/zone string Europe/Kiev
d-i clock-setup/ntp boolean true

# Packages, Mirrors, Image
d-i mirror/country string UA
d-i apt-setup/multiverse boolean true
d-i apt-setup/restricted boolean true
d-i apt-setup/universe boolean true
d-i pkgsel/update-policy select unattended-upgrades
# Automatically download and install stable updates?
unattended-upgrades	unattended-upgrades/enable_auto_updates	boolean	true

# Users
d-i passwd/user-fullname string user
d-i passwd/username string user
#d-i passwd/user-password-crypted password userEncryptedPassword
d-i passwd/root-login boolean false
#d-i passwd/root-password-crypted password rootEncryptedPasswd
d-i user-setup/allow-password-weak boolean true

# Add the initial user to the audio group as well as the usual ones, since
# realtime audio for jack is not PolicyKit aware yet, and users cannot run
# jack with realtime priority without being in this group.
d-i passwd/user-default-groups string adm dialout cdrom sudo dip lpadmin sudo plugdev sambashare audio video wireshark vboxusers

# Grub
d-i grub-installer/skip boolean true
d-i lilo-installer/skip boolean true
ubiquity ubiquity/install_bootloader boolean false

# Complete installation
d-i prebaseconfig/reboot_in_progress note
ubiquity ubiquity/reboot    boolean false
ubiquity ubiquity/poweroff  boolean false


# ========================================
# Only show Ubuntu Studio tasks.
tasksel	tasksel/limit-tasks	string minimal, standard, ubuntustudio-generation, ubuntustudio-recording, ubuntustudio-audio-plugins, ubuntustudio-desktop, ubuntustudio-graphics, ubuntustudio-video

# Enable real-time process priority in jackd.
jackd2	jackd/tweak_rt_limits	boolean true
