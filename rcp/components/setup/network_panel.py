import os

from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from rcp.network.networkmanager import get_all_network_interface_names, get_profile_by_id, get_psk, \
    get_ssid, get_connection_method, activate_connection, deactivate_connection, enable_wifi, disable_wifi, get_ipv4

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NetworkPanel(BoxLayout):
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

        self.profile = get_profile_by_id()
        self.wpa_psk = get_psk(self.profile)
        self.wpa_ssid = get_ssid(self.profile)
        self.connection_method = get_connection_method(self.profile)
        self.apply_thread = None
        self.disable_thread = None
        self.refresh_task = Clock.schedule_interval(self.refresh_thread, 1)

    def refresh_thread(self, *args):
        address, netmask, gateway = get_ipv4(self.profile)
        self.address = address
        self.netmask = netmask
        self.gateway = gateway
        # self.status_text = self.status_text + "A"

    def activate_connection(self, *args):
        activate_connection(self.profile)
        self.status_text = "Connection Ready"

    def enable_wifi(self, *args):
        self.status_text = "Enabling Wifi Device"
        enable_wifi()
        self.status_text = "Enabling Connection"
        Clock.schedule_once(self.activate_connection, timeout=2)

    def apply(self):
        Clock.schedule_once(self.enable_wifi)

    def disable(self):
        disable_wifi()

    def get_all_network_interfaces(self):
        return get_all_network_interface_names()
