import os
import time

import nmcli
import threading


from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

nmcli.disable_use_sudo()

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NetworkPanel(BoxLayout):
    networks = ListProperty(["Loading"])
    network = StringProperty("")
    devices = ListProperty(["Loading"])
    device = StringProperty("")
    address = StringProperty("")
    netmask = StringProperty("")
    gateway = StringProperty("")
    wpa_psk = StringProperty("")
    status_text = StringProperty("Ready")
    wifi_enabled = BooleanProperty(False)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))

        self.wpa_psk = "psk"
        self.apply_thread = None
        self.disable_thread = None
        self.wifi_enabled = nmcli.radio().wifi

        # Clock.schedule_once(self.scan_thread, 0)
        threading.Thread(target=self.scan_thread).start()

    @mainthread
    def log(self, message: str):
        log.info(message)
        self.status_text += f"{message}\n"

    def scan_thread(self, *args, **kv):
        self.log("Request Wifi Rescanning")
        self.update_devices([item.device for item in nmcli.device() if item.device_type in ["wifi"]])

        time.sleep(5)
        if self.wifi_enabled:
            try:
                status = nmcli.general.status()
                self.log(f"{status.state.value} {status.connectivity.value} {status.wifi}")
            except Exception as e:
                log.error(e.__str__())

            nmcli.device.wifi_rescan()
            self.update_networks(list(set([item.ssid for item in nmcli.device.wifi()])))
        self.update_connection_properties()

    def connect_thread(self, *args, **kv):
        self.log("Request Wifi Connection")
        if self.network in [item.name for item in nmcli.connection()]:
            log.info(f"Found existing profile for {self.network}, deleting")
            nmcli.connection.delete(name=self.network)
            time.sleep(2)
            log.info(f"Creating new wifi connection for: {self.network}")
            nmcli.device.wifi_connect(ssid=self.network, password=self.wpa_psk, ifname=self.device)
        try:
        except Exception as e:
            log.info(f"Error creating connection {self.network}: {e.__str__()}")
            return

        self.update_devices([item.device for item in nmcli.device() if item.device_type in ["wifi"]])
        self.update_networks(list(set([item.ssid for item in nmcli.device.wifi()])))
        self.update_connection_properties()
        self.log("Connection reconfigured")

    def on_wifi_enabled(self, instance, value):
        if self.wifi_enabled:
            self.log("Enable Wifi Connections")
            nmcli.radio.wifi_on()
            threading.Thread(target=self.scan_thread).start()
        else:
            self.log("Disable Wifi Connections")
            nmcli.radio.wifi_off()

    @mainthread
    def update_devices(self, items):
        self.devices = items
        if len(self.devices) > 0:
            self.device = self.devices[0]

    @mainthread
    def update_networks(self, items):
        self.networks = items

    @mainthread
    def on_device(self, instance, value):
        self.update_connection_properties()

    @mainthread
    def update_connection_properties(self):
        device_status = nmcli.device.show(self.device)
        connection_name = device_status.get("GENERAL.CONNECTION", None)
        if connection_name is None:
            self.log(f"No connection configured")
            self.wpa_psk = ""
            self.address = ""
            self.gateway = ""
            self.network = ""
            return

        self.log(f"Found connection: {connection_name}")
        connection_status = nmcli.connection.show(name=connection_name, show_secrets=True)
        self.network = connection_status.get('802-11-wireless.ssid', "")
        self.wpa_psk = connection_status.get('802-11-wireless-security.psk', "")
        if "100" in device_status.get("GENERAL.STATE"):
            self.address = device_status.get('IP4.ADDRESS[1]', "")
            self.gateway = device_status.get('IP4.GATEWAY', "")
        else:
            self.address = ""
            self.gateway = ""


    def apply(self):
        threading.Thread(target=self.connect_thread).start()
