import asyncio
import os

import nmcli

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, ColorProperty
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.lang import Builder

nmcli.disable_use_sudo()

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class SsidPopup(ModalView):
    container: GridLayout = ObjectProperty()
    callback = ObjectProperty()
    current_value = StringProperty()
    available_networks = ListProperty()
    selected_network = StringProperty()
    scanning = BooleanProperty(False)

    def __init__(self, callback, selected_network, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)
        self.selected_network = selected_network
        self.callback = callback
        self.container: GridLayout = self.ids['container']
        self.schedule_scan()

    def select_network(self, button):
        self.selected_network = button.text

        for b in self.container.children:
            if b is button:
                b.background_color = self.app.formats.color_on
            else:
                b.background_color = self.app.formats.color_off

    async def wifi_rescan(self, *args, **kv):
        self.scanning = True
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, nmcli.device.wifi_rescan)
            found_networks = await loop.run_in_executor(None, nmcli.device.wifi)
            raw_networks = [item for item in found_networks]
            available_networks = {item.ssid: item for item in raw_networks if len(item.ssid) > 0}

            # Cleanup all children if any exists
            self.container.clear_widgets()

            for net in available_networks.values():
                btn = Button(
                    text=net.ssid,
                    on_release=self.select_network,
                    background_color=self.app.formats.color_on if net.ssid == self.selected_network else self.app.formats.color_off,
                    height=40,
                    size_hint_x=1,
                    size_hint_y=None,
                )
                self.container.add_widget(btn)

        except Exception as e:
            log.info(e.__str__())

        finally:
            self.scanning = False

    def schedule_scan(self):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.wifi_rescan()))

    def apply(self):
        log.info(f"Received: {self.selected_network}")
        self.callback(self.selected_network)
        self.dismiss()
