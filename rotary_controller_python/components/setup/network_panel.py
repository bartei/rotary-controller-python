import os

from kivy.properties import StringProperty, BooleanProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from rotary_controller_python.network import read_interfaces, render_interfaces, reload_interfaces
from rotary_controller_python.network.models import NetworkInterface, Wireless

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NetworkPanel(BoxLayout):
    device = StringProperty("")
    dhcp = BooleanProperty(False)
    address = StringProperty("")
    netmask = StringProperty("")
    gateway = StringProperty("")
    wpa_ssid = StringProperty("")
    wpa_psk = StringProperty("")
    status_text = StringProperty("Ready")

    def __init__(self, **kv):
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))

        configuration: NetworkInterface = read_interfaces()
        self.device = configuration.name
        self.dhcp = configuration.dhcp
        if configuration.wireless is not None:
            if configuration.wireless.ssid is not None:
                self.wpa_ssid = configuration.wireless.ssid
            if configuration.wireless.password is not None:
                self.wpa_psk = configuration.wireless.password

        if configuration.address is not None and len(configuration.address) > 0:
            self.address = configuration.address

        if configuration.netmask is not None:
            self.netmask = str(configuration.netmask)

        if configuration.gateway is not None and len(configuration.gateway) > 0:
            self.gateway = configuration.gateway

    def confirm(self):
        try:
            configuration = NetworkInterface(
                name=self.device,
                dhcp=self.dhcp,
                address=self.address if not self.dhcp else None,
                gateway=self.gateway if not self.dhcp else None,
                netmask=int(self.netmask) if not self.dhcp else None,
                wireless=Wireless(
                    password=self.wpa_psk,
                    ssid=self.wpa_ssid
                )
            )
            render_interfaces(configuration=configuration)
            status = reload_interfaces()
        except Exception as e:
            log.exception(e.__str__())
            status = e.__str__()

        self.status_text = status

    def test_configuration(self):
        try:
            configuration = NetworkInterface(
                name=self.device,
                dhcp=self.dhcp,
                address=self.address if not self.dhcp else None,
                gateway=self.gateway if not self.dhcp else None,
                netmask=int(self.netmask) if not self.dhcp else None,
                wireless=Wireless(
                    password=self.wpa_psk,
                    ssid=self.wpa_ssid
                )
            )
            render_interfaces(configuration=configuration)
            status = reload_interfaces()
        except Exception as e:
            status = e.__str__()
        self.status_text = status
