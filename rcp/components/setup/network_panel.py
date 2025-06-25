import os
import threading

import nmcli
import threading


from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# from rcp.network.networkmanager import get_all_network_interface_names, get_profile_by_id, get_psk, \
#     get_ssid, get_connection_method, activate_connection, deactivate_connection, enable_wifi, disable_wifi, get_ipv4

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
    wpa_ssid = StringProperty("")
    wpa_psk = StringProperty("")
    status_text = StringProperty("Ready")
    profile = ObjectProperty()
    connection_method = StringProperty("")
    refresh_task = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))

        self.profile = "profile"
        self.wpa_psk = "psk"
        self.wpa_ssid = "ssid"
        self.connection_method = "method"
        self.apply_thread = None
        self.disable_thread = None
        self.refresh_task = Clock.schedule_interval(self.refresh_thread, 1)
        # Clock.schedule_once(self.scan_thread, 0)
        threading.Thread(target=self.scan_thread).start()

    def scan_thread(self, *args, **kv):
        self.update_devices([item.device for item in nmcli.device() if item.device_type in ["wifi"]])
        self.update_networks(list(set([item.ssid for item in nmcli.device.wifi()])))
        # self.networks =

    @mainthread
    def update_devices(self, items):
        self.devices = items

    @mainthread
    def update_networks(self, items):
        self.networks = items

    def refresh_thread(self, *args):
        self.address = "address"
        self.netmask = "netmask"
        self.gateway = "gateway"
        # self.status_text = self.status_text + "A"

    def activate_connection(self, *args):
        self.status_text = "Connection Ready"

    def enable_wifi(self, *args):
        self.status_text = "Enabling Wifi Device"
        self.status_text = "Enabling Connection"
        Clock.schedule_once(self.activate_connection, timeout=2)

    def apply(self):
        Clock.schedule_once(self.enable_wifi)

    def disable(self):
        pass

    def get_all_network_interfaces(self):
        return "merda"
