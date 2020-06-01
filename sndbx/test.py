print("@ module name:", __name__)

import sys
print(sys.path)

from studioinstaller.spawned import SpawnedSU, Spawned, ask_user
from studioinstaller.partition import StandardPV, Disk, LuksPV, LvmOnLuksVG, LvmLV
from studioinstaller.partition.base import VType
from studioinstaller.spawned import logger as log
import re, io
import inspect

# Spawned.enable_logging()
# print(dir(log))
# log.header_s()
# log.header()

disk = Disk("sdr")
partition = StandardPV('134', "/var").on(disk)
partition_id = ''.join([ch for ch in partition.id if ch.isdigit()])
print(partition.id, partition_id)
