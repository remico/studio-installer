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

# disk = Disk("sdr")
# partition = StandardPV('134', "/var").on(disk)
# partition_id = ''.join([ch for ch in partition.id if ch.isdigit()])
# print(partition.id, partition_id)


# def foo(a, **kw):
#     print("foo", a, kw)
#     foo_zoo(**kw)
#
#
# def foo_zoo(c, **kw):
#     print("foo_zoo", c, kw)
#
#
# def zoo(a, b, **kw):
#     print("zoo", a, b, kw)
#
#
# def bar(**kw):
#     print("========")
#     foo(**kw)
#     zoo(**kw)
#     print("bar", kw)
#
#
# for i in range(3):
#     bar(a=1, b=2, c=3, d=4)
