__version__ = '0.1.0'

import os.path
from enum import Enum
from datetime import datetime

import dbus

bus = dbus.SystemBus()


class State(Enum):
    """https://upower.freedesktop.org/docs/Device.html#Device:State"""
    UNKNOWN = 0
    CHARGING = 1
    DISCHARGING = 2
    EMPTY = 3
    FULLY_CHARGED = 4
    PENDING_CHARGE = 5
    PENDING_DISCHARGE = 6


def enumerate_devices():
    upower = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
    return upower.EnumerateDevices(dbus_interface='org.freedesktop.UPower')


def get_device(identifier=None, short_name=None):
    if not identifier or short_name:
        return None
    b = bus.get_object(
        'org.freedesktop.UPower',
        identifier or f'/org/freedesktop/UPower/devices/{short_name}'
    )
    return dbus.Interface(b, dbus_interface='org.freedesktop.UPower.Device')


def short_name(device_path):
    return os.path.basename(device_path)


def get_devices():
    return {
        short_name(dev): get_device(dev)
        for dev in enumerate_devices()
    }


def _history_to_tuple(dbus_array):
    return [
        (datetime.utcfromtimestamp(i[0]), i[1], State(i[2]))
        for i in dbus_array
    ]


def get_rate(battery, seconds=0, points=1000000):
    return _history_to_tuple(battery.GetHistory('rate', seconds, points))


def get_charge(battery, seconds=0, points=1000000):
    return _history_to_tuple(battery.GetHistory('charge', seconds, points))
