import os

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.settings import SettingNumeric, SettingSpacer
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from loguru import logger as log
from kivy.uix.popup import Popup
from kivy.lang import Builder

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoPanel(BoxLayout):
    servo = ObjectProperty()

    def __init__(self, servo, **kv):
        self.servo = servo
        super().__init__(**kv)


class ScalePanel(BoxLayout):
    scale = ObjectProperty()

    def __init__(self, scale, **kv):
        self.scale = scale
        super().__init__(**kv)


class NumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0)

    def validate(self, value):
        try:
            if "." in value:
                self.value = float(value)
            else:
                self.value = int(value)
        except Exception as e:
            log.error(e.__str__())


class StringItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty("")


class Setup(Popup):
    tabbed_panel = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.tabbed_panel: TabbedPanel
        app = App.get_running_app()
        panes = []
        for i in range(4):
            pane = TabbedPanelItem(text=f"Panel {i}")
            pane.add_widget(ScalePanel(scale=app.home.coord_bars[i]))
            self.tabbed_panel.add_widget(pane)
            panes.append(pane)

        pane = TabbedPanelItem(text=f"Servo")
        pane.add_widget(ServoPanel(servo=app.home.servo))
        self.tabbed_panel.add_widget(pane)
        panes.append(pane)
        self.tabbed_panel.default_tab = panes[0]

