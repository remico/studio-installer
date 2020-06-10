print("@ module name:", __name__)

import sys
print(sys.path)

from studioinstaller.spawned import SpawnedSU, Spawned, ask_user
from studioinstaller.partition import PlainPV, Disk, LuksPV, LvmOnLuksVG, LvmLV
from studioinstaller.partition.base import VType
from studioinstaller.spawned import logger as log
import re, io
import inspect

Spawned.enable_logging()
# Spawned.enable_debug_commands()

SpawnedSU.do("df | grep /dev")

