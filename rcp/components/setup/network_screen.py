import asyncio
import os
import nmcli

from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from kivy.lang import Builder

nmcli.disable_use_sudo()

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class NetworkScreen(Screen):
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
        try:
            self.wifi_enabled = nmcli.radio().wifi
        except FileNotFoundError:
            log.warning("nmcli not found, network features will be disabled.")
            self.wifi_enabled = False

        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.refresh()))
        self.status_update_task = Clock.schedule_interval(lambda dt: asyncio.ensure_future(self.status_update()), timeout=1)

    def log(self, message: str):
        log.info(message)
        self.status_text += f"{message}\n"

    async def status_update(self):
        if not self.wifi_enabled:
            return
        if self.device != "":
            data = await asyncio.to_thread(nmcli.device.show, self.device)
            new_state = data.get("GENERAL.STATE")
            if self.state != new_state:
                self.log("State Changed, refreshing properties")
                await self.refresh()

    async def refresh(self):
        if not self.wifi_enabled:
            self.log("nmcli not available, network features disabled")
            return
        log.debug("Refresh properties invoked")

        # Scan Devices
        all_devices = await asyncio.to_thread(nmcli.device)
        self.devices = [item.device for item in all_devices if item.device_type in ["wifi"]]
        if len(self.devices) > 0:
            self.device = self.devices[0]
        else:
            self.device = ""

        await asyncio.sleep(0.5)

        # If we have a device, read the current settings
        if self.device != "":
            data = await asyncio.to_thread(nmcli.device.show, self.device)

            self.device = data.get("GENERAL.DEVICE") or self.device
            self.hwaddr = data.get("GENERAL.HWADDR") or self.hwaddr
            self.state = data.get("GENERAL.STATE") or self.state
            self.address = data.get("IP4.ADDRESS[1]") or ""
            self.gateway = data.get("IP4.GATEWAY") or ""
            self.dns = data.get("IP4.DNS[1]") or ""
            self.connection = data.get("GENERAL.CONNECTION") or ""

            if data.get("GENERAL.CONNECTION", None) is not None:
                try:
                    conn = await asyncio.to_thread(nmcli.connection.show, name=self.connection, show_secrets=True)
                    self.key_mgmt = conn.get('802-11-wireless-security.key-mgmt') or ""
                    self.wireless_mode = conn.get('802-11-wireless.mode') or ""
                    self.wireless_auth_alg = conn.get('802-11-wireless-security.auth-alg') or ""
                    self.password = conn.get('802-11-wireless-security.psk') or ""
                except Exception as e:
                    log.error(e.__str__())
            else:
                self.key_mgmt = ""
                self.wireless_mode = ""
                self.wireless_auth_alg = ""
                self.password = ""

        self.lock = False

    async def connect(self):
        if not self.wifi_enabled:
            self.log("nmcli not available, network features disabled")
            return        
        self.log("Request Wifi Connection")

        connections_dict = await asyncio.to_thread(nmcli.connection)
        if self.connection in [item.name for item in connections_dict]:
            connection = self.connection
            self.log(f"Updating the password for connection: {self.connection}")
            new_options = {
                '802-11-wireless-security.psk': self.password
            }
            try:
                await asyncio.to_thread(nmcli.device.show, self.device)
                await asyncio.sleep(5)
                await asyncio.to_thread(nmcli.connection.modify, name=connection, options=new_options)
                await asyncio.sleep(5)
                await asyncio.to_thread(nmcli.connection.up, name=connection)
                await asyncio.sleep(5)
            except Exception as e:
                self.log(f"Unable to edit connection: {e.__str__()}")
        else:
            self.log(f"Creating a new connection profile for {self.connection} with device: {self.device}")
            try:
                await asyncio.to_thread(
                    nmcli.device.wifi_connect,
                    ssid=self.connection,
                    password=self.password,
                    ifname=self.device
                )
            except Exception as e:
                self.log(f"Unable to connect: {e.__str__()}")

    def on_wifi_enabled(self, instance, value):
        try:
            if self.wifi_enabled:
                self.log("Enable Wifi Connections")
                nmcli.radio.wifi_on()
                self.log("Run Scan to find the available access points")
            else:
                self.log("Disable Wifi Connections")
                nmcli.radio.wifi_off()
        except FileNotFoundError:
            log.warning("nmcli not found, network features will be disabled.")
            self.wifi_enabled = False
        
    def apply(self):
        self.lock = True
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.connect()))

    def select_network(self, selected_network):
        log.info(f"Selected network: {selected_network}")
        self.connection = selected_network

    def on_dismiss(self):
        log.debug("Dismiss signal received, stopping status_update_task")
        self.status_update_task.cancel()
