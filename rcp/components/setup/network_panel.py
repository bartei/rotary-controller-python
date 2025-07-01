import os
import time

import nmcli
import threading

from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from pydantic import BaseModel

nmcli.disable_use_sudo()

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class DeviceProperties(BaseModel):
    device: str = ""
    type: str = ""
    hwaddr: str = ""
    state: str = ""
    connection: str = ""
    address: str = ""
    gateway: str = ""
    dns: str = ""
    domain: str = ""
    password: str = ""
    key_mgmt: str = ""
    wireless_mode: str = ""
    wireless_auth_alg: str = ""


class NetworkPanel(BoxLayout):
    setup_popup = ObjectProperty()
    networks = ListProperty(["Loading"])
    connection = StringProperty("")
    devices = ListProperty(["Loading"])
    device = StringProperty("")
    state = StringProperty("")
    address = StringProperty("")
    netmask = StringProperty("")
    gateway = StringProperty("")
    dns = StringProperty("")
    password = StringProperty("")
    key_mgmt = StringProperty("")
    hwaddr = StringProperty("")
    wireless_auth_alg = StringProperty("")
    wireless_mode = StringProperty("")
    lock = BooleanProperty(True)

    status_text = StringProperty("")
    wifi_enabled = BooleanProperty(False)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))
        self.wifi_enabled = nmcli.radio().wifi

        # Clock.schedule_once(self.scan_thread, 0)
        threading.Thread(target=self.refresh_thread).start()
        self.status_update_task = Clock.schedule_interval(self.status_update_thread, timeout=1)

    @mainthread
    def log(self, message: str):
        log.info(message)
        self.status_text += f"{message}\n"

    def status_update_thread(self, *args, **kv):
        if self.device != "":
            data = nmcli.device.show(self.device)
            new_state = data.get("GENERAL.STATE")
            if self.state != new_state:
                self.log("State Changed, refreshing properties")
                self.refresh_thread()

    def refresh_thread(self):
        log.debug("Refresh properties thread invoked")

        # Scan Devices
        devices = [item.device for item in nmcli.device() if item.device_type in ["wifi"]]
        self.update_devices(devices)
        time.sleep(0.5)

        # If we have a device, read the current settings
        if self.device != "":
            data = nmcli.device.show(self.device)
            device_properties = DeviceProperties()

            if data.get("GENERAL.DEVICE") is not None:
                device_properties.device = data.get("GENERAL.DEVICE")
            if data.get("GENERAL.HWADDR") is not None:
                device_properties.hwaddr = data.get("GENERAL.HWADDR")
            if data.get("GENERAL.TYPE") is not None:
                device_properties.type = data.get("GENERAL.TYPE")
            if data.get("GENERAL.STATE") is not None:
                device_properties.state = data.get("GENERAL.STATE")
            if data.get("IP4.ADDRESS[1]") is not None:
                device_properties.address = data.get("IP4.ADDRESS[1]")
            if data.get("IP4.GATEWAY") is not None:
                device_properties.gateway = data.get("IP4.GATEWAY")
            if data.get("IP4.DNS[1]") is not None:
                device_properties.dns = data.get("IP4.DNS[1]")
            if data.get("IP4.DOMAIN[1]") is not None:
                device_properties.domain = data.get("IP4.DOMAIN[1]")
            if data.get("GENERAL.CONNECTION") is not None:
                device_properties.connection = data.get("GENERAL.CONNECTION")

                conn = nmcli.connection.show(name=device_properties.connection, show_secrets=True)
                device_properties.key_mgmt = conn.get('802-11-wireless-security.key-mgmt', "")
                device_properties.wireless_mode = conn.get('802-11-wireless.mode', "")
                device_properties.wireless_auth_alg = conn.get('802-11-wireless-security.auth-alg', "")
                device_properties.password = conn.get('802-11-wireless-security.psk', "")
            self.update_properties(**device_properties.model_dump())

        self.lock = False

    def connect_thread(self, *args, **kv):
        self.log("Request Wifi Connection")
        if self.connection in [item.name for item in nmcli.connection()]:
            connection = nmcli.connection.show(name=self.connection, show_secrets=True)
            self.log(f"Updating the password for connection: {self.connection}")
            new_options = {
                '802-11-wireless-security.psk': self.password
            }
            try:
                nmcli.connection.down(name=self.connection)
                time.sleep(5)
                nmcli.connection.modify(name=self.connection, options=new_options)
                time.sleep(5)
                nmcli.connection.up(name=self.connection)
            except Exception as e:
                self.log(f"Unable to edit connection: {e.__str__()}")
        else:
            self.log(f"Creating a new connection profile for {self.connection} with device: {self.device}")
            try:
                nmcli.device.wifi_connect(ssid=self.connection, password=self.password, ifname=self.device)
            except Exception as e:
                self.log(f"Unable to connect: {e.__str__()}")


    def on_wifi_enabled(self, instance, value):
        if self.wifi_enabled:
            self.log("Enable Wifi Connections")
            nmcli.radio.wifi_on()
            self.log("Run Scan to find the available access points")
        else:
            self.log("Disable Wifi Connections")
            nmcli.radio.wifi_off()

    @mainthread
    def update_properties(self, **properties):
        for k, v in [item for item in properties.items() if item[1] is not None]:
            self.__setattr__(k, v)

    @mainthread
    def update_devices(self, items):
        self.devices = items
        if len(self.devices) > 0:
            self.device = self.devices[0]
        else:
            self.device = ""

    @mainthread
    def update_networks(self, items):
        self.networks = items

    def apply(self):
        self.lock = True
        threading.Thread(target=self.connect_thread).start()

    def scan(self):
        threading.Thread(target=self.scan_thread).start()

    def scan_thread(self):
        if self.wifi_enabled:
            try:
                nmcli.device.wifi_rescan()
                self.update_networks(list(set([item.ssid for item in nmcli.device.wifi()])))
            except Exception as e:
                self.log(e.__str__())

    def on_dismiss(self, instance, value):
        log.debug("Dismiss signal received, stopping status_update_task")
        self.status_update_task.cancel()