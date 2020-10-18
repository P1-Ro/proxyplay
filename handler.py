import re

import cec
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject

from config import MAC_ADDRESS, SHUTDOWN_TIMEOUT

PROPERTIES = "org.freedesktop.DBus.Properties"

c
class Handler:
    def __init__(self):
        self.event_id = None

        DBusGMainLoop(set_as_default=True)

        cec.init()
        self.sound_bar = cec.Device(cec.CECDEVICE_AUDIOSYSTEM)

        self.bus = dbus.SystemBus()
        self.address = '/org/bluez/hci0/dev_' + MAC_ADDRESS.replace(":", "_")
        self.proxy = self.bus.get_object('org.bluez', self.address)

        self.device = dbus.Interface(self.proxy, "org.bluez.Device1")
        self.device.connect_to_signal("PropertiesChanged", self.handle_device_change, dbus_interface=PROPERTIES)

        self.init_loop()

    def init_loop(self):
        fd_string = self.proxy.Introspect()
        matcher = re.search("node name=\"(fd\\d+)\"", fd_string)
        fd = None
        if matcher:
            fd = matcher.group(1)
            print(fd)

        proxy = self.bus.get_object('org.bluez', self.address + "/" + fd)
        player = dbus.Interface(proxy, "org.bluez.MediaTransport1")
        player.connect_to_signal("PropertiesChanged", self.handle_media_change, dbus_interface=PROPERTIES)

        GObject.MainLoop().run()

    def power_on(self, event):
        cec.set_active_source()
        if event is not None:
            GObject.source_remove(event)

    def power_off(self):
        self.sound_bar.standby()

    def handle_device_change(self, iface, obj, params):
        if "Connected" in obj:
            if obj["Connected"]:
                self.init_loop()
            else:
                self.device.Connect()

    def handle_media_change(self, iface, obj, params):
        if "State" in obj:
            if obj["State"] == "active":
                self.power_on(self.event_id)
            elif obj["State"] == "idle":
                self.event_id = GObject.timeout_add_seconds(SHUTDOWN_TIMEOUT, self.power_off)


if __name__ == '__main__':
    handler = Handler()
