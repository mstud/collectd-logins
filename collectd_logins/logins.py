import collectd
import datetime
import utmp
from plugin import PLUGIN_NAME, INTERVAL, LOGINS_WINDOW

try:
    import psutil
except ImportError:
    collectd.error(
        "{} plugin: python package 'psutil' not installed. Plugin will not work properly.".format(PLUGIN_NAME))


def get_login_data():
    now = datetime.datetime.now()
    count = 0
    failed = 0
    with open("/var/log/wtmp", 'rb') as fd:
        buf = fd.read()
        for entry in utmp.read(buf):
            if entry.time > now - LOGINS_WINDOW:
                count += 1
    with open("/var/log/btmp", 'rb') as fd:
        buf = fd.read()
        for entry in utmp.read(buf):
            if entry.time > now - LOGINS_WINDOW:
                failed += 1
    return (count, failed)


def get_session_data():
    users = psutil.users()
    total = len(users)
    uniq = set([entry.name for entry in users])
    unique_users = len(uniq)
    return (unique_users, total)


def read():
    unique_users, total = get_session_data()
    logins, failed_logins = get_login_data()

    data = [
        ("sessions", "unique_users", unique_users),
        ("sessions", "total", total),
        ("logins", "total_last_hour", logins),
        ("logins", "failed_last_hour", failed_logins)

    ]

    for (name, value_type, value) in data:
        val = collectd.Values(
            type=value_type,
            plugin=PLUGIN_NAME,
            plugin_instance=name,
            values=[value])
        collectd.debug('{} plugin: {} = {}'.format(
            PLUGIN_NAME, value_type, value))
        val.dispatch()


def config(conf):
    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]
        if key == "interval":
            INTERVAL = val
        elif key == "window":
            LOGINS_WINDOW = datetime.timedelta(seconds=val)

        collectd.debug('{} plugin config: {} = {}'.format(
            PLUGIN_NAME, key, val))
    collectd.register_read(read, INTERVAL)


collectd.register_config(config)
