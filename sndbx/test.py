print("@ module name:", __name__)

import sys
print(sys.path)

from studioinstaller.spawned import SpawnedSU, Spawned, ask_user
from studioinstaller.partition import PlainPV, Disk, LuksPV, LvmOnLuksVG, LvmLV, CryptVV
from studioinstaller.partition.base import VType
from studioinstaller.spawned import logger as log
from studioinstaller import util
import re, io
import inspect
from studioinstaller.configfile import IniConfig, FstabLine, FstabConfig

Spawned.enable_logging()
Spawned.enable_debug_commands()

# disk = Disk("/dev/sdb")
# luks = LuksPV(1).on(disk)
# p1 = CryptVV("home").on(luks)
# print(util.is_trim_supported(p1))

f = FstabConfig("/tmp/qq")
f.append("UUID=11212-12-13", "/ee/dd", "ext3", "defaults")
f.append(FstabLine("UUID=11212-12-12", "/ee/dd", "ext3", "defaults"))
# f.apply(r"qq1", "bla")
Spawned.do("cat /tmp/qq")
