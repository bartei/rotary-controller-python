import os
import logging

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.app import App

log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))

if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ToolbarButton(Button):
    pass


class Toolbar(BoxLayout):
    current_units = StringProperty()

    def toggle_units(self, *args, **kv):
        app = App.get_running_app()
        if app.current_units == "in":
            app.current_units = "mm"
        else:
            app.current_units = "in"
