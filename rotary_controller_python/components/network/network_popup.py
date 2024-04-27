import os

from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.lang import Builder

from rotary_controller_python.network import read_interfaces, render_interfaces, reload_interfaces
from rotary_controller_python.network.models import NetworkInterface, Wireless

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NetworkPopup(Popup):
    device = ObjectProperty(None)
    dhcp = ObjectProperty(None)
    address = ObjectProperty(None)
    netmask = ObjectProperty(None)
    gateway = ObjectProperty(None)
    wpa_ssid = ObjectProperty(None)
    wpa_psk = ObjectProperty(None)
    status_text = ObjectProperty(None)

    def on_open(self):
        configuration: NetworkInterface = read_interfaces()
        self.device.text = configuration.name
        self.dhcp.pressed = configuration.dhcp
        if configuration.wireless is not None:
            if configuration.wireless.ssid is not None:
                self.wpa_ssid.text = configuration.wireless.ssid
            if configuration.wireless.password is not None:
                self.wpa_psk.text = configuration.wireless.password

        if configuration.address is not None and len(configuration.address) > 0:
            self.address.text = configuration.address

        if configuration.netmask is not None:
            self.netmask.text = str(configuration.netmask)

        if configuration.gateway is not None and len(configuration.gateway) > 0:
            self.gateway.text = configuration.gateway

    def confirm(self):
        configuration = NetworkInterface(
            name=self.device.text,
            dhcp=self.dhcp.pressed,
            address=self.address.text if not self.dhcp.pressed else None,
            gateway=self.gateway.text if not self.dhcp.pressed else None,
            netmask=int(self.netmask.text) if not self.dhcp.pressed else None,
            wireless=Wireless(
                password=self.wpa_psk.text,
                ssid=self.wpa_ssid.text
            )
        )
        render_interfaces(configuration=configuration)
        self.dismiss()

    def cancel(self):
        self.dismiss()

    def test_configuration(self):
        try:
            configuration = NetworkInterface(
                name=self.device.text,
                dhcp=self.dhcp.pressed,
                address=self.address.text if not self.dhcp.pressed else None,
                gateway=self.gateway.text if not self.dhcp.pressed else None,
                netmask=int(self.netmask.text) if not self.dhcp.pressed else None,
                wireless=Wireless(
                    password=self.wpa_psk.text,
                    ssid=self.wpa_ssid.text
                )
            )
            render_interfaces(configuration=configuration)
            status = reload_interfaces()
        except Exception as e:
            status = e.__str__()
        self.status_text.text = status
