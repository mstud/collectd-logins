import datetime
import struct
import collectd
from collections import namedtuple
from plugin import PLUGIN_NAME

try:
    from enum import Enum
except ImportError:
    collectd.error(
        "{} plugin: python package 'enum34' not installed. Plugin will not work properly.".format(PLUGIN_NAME))


class UTmpRecordType(Enum):
    empty = 0
    run_lvl = 1
    boot_time = 2
    new_time = 3
    old_time = 4
    init_process = 5
    login_process = 6
    user_process = 7
    dead_process = 8
    accounting = 9


def convert_string(val):
    if isinstance(val, bytes):
        return val.rstrip(b'\0').decode("utf-8").encode("ascii","ignore")
    return val


class UTmpRecord(namedtuple('UTmpRecord',
                            'type pid line id user host exit0 exit1 session' +
                            ' sec usec addr0 addr1 addr2 addr3 unused')):
    @property
    def type(self):
        return UTmpRecordType(self[0])

    @property
    def time(self):
        return datetime.datetime.fromtimestamp(self.sec) + datetime.timedelta(microseconds=self.usec)


STRUCT = struct.Struct('hi32s4s32s256shhiii4i20s')


def read(buf):
    offset = 0
    while offset < len(buf):
        yield UTmpRecord._make(map(convert_string, STRUCT.unpack_from(buf, offset)))
        offset += STRUCT.size
