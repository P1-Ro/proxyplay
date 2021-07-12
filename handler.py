import re
import time
import logging
import cec
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from systemd.journal import JournaldLogHandler

from config import MAC_ADDRESS, SHUTDOWN_TIMEOUT

PROPERTIES = "org.freedesktop.DBus.Properties"

# get an instance of the logger object this module will use
logger = logging.getLogger(__name__)

# instantiate the JournaldLogHandler to hook into systemd
journald_handler = JournaldLogHandler()

# set a formatter to include the level name
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))

# add the journald handler to the current logger
logger.addHandler(journald_handler)

# optionally set the logging level
logger.setLevel(logging.DEBUG)


class Handler:
    def __init__(self):
        self.event_id = None
        self.current_fd = None

        DBusGMainLoop(set_as_default=True)

        cec.init()
        self.sound_bar = cec.Device(cec.CECDEVICE_AUDIOSYSTEM)

        self.bus = dbus.SystemBus()
        self.address = '/org/bluez/hci0/dev_' + MAC_ADDRESS.replace(":", "_")
        self.proxy = self.bus.get_object('org.bluez', self.address)

        self.device = dbus.Interface(self.proxy, "org.bluez.Device1")
        self.device.connect_to_signal("PropertiesChanged", self.handle_device_change, dbus_interface=PROPERTIES)
        self.init_loop()

        GLib.MainLoop().run()

    def init_loop(self):
        fd_string = self.proxy.Introspect()
        matcher = re.search("node name=\"(fd\\d+)\"", fd_string)

        if matcher:
            fd = matcher.group(1)
            logger.info("device with file-descriptor: %s connected", fd)

            if self.current_fd != fd:
                logger.info("replacing old file-descriptor: %s with new one: %s", self.current_fd, fd)

                self.current_fd = fd
                proxy = self.bus.get_object('org.bluez', self.address + "/" + self.current_fd)
                player = dbus.Interface(proxy, "org.bluez.MediaTransport1")
                player.connect_to_signal("PropertiesChanged", self.handle_media_change, dbus_interface=PROPERTIES)
        else:
            logger.info("no device connected")

    def power_on(self):
        cec.set_active_source()
        if self.event_id is not None:
            GLib.source_remove(self.event_id)
            self.event_id = None

    def power_off(self):
        self.sound_bar.standby()
        self.event_id = None
        return False

    def handle_device_change(self, iface, obj, params):
        logger.info(obj)
        if bool(obj["Connected"]):
            time.sleep(SHUTDOWN_TIMEOUT)
            self.init_loop()

    def handle_media_change(self, iface, obj, params):
        if "State" in obj:
            logger.info(obj["State"])
            if obj["State"] == "active":
                self.power_on()
            elif obj["State"] == "idle":
                self.event_id = GLib.timeout_add_seconds(SHUTDOWN_TIMEOUT, self.power_off)


if __name__ == '__main__':
    handler = Handler()
