import os
from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file {kv_file}")
    Builder.load_file(kv_file)


class CustomPopup(BoxLayout):
    title = StringProperty("")
    message = StringProperty("")
    button_text = StringProperty("OK")
    on_dismiss_callback = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._popup = Popup(
            title=self.title,
            content=self,
            size_hint=(0.6, 0.5),
            auto_dismiss=False,
        )

    def open(self):
        self._popup.title = self.title
        self._popup.open()

    def dismiss(self):
        self._popup.dismiss()

    def on_button_press(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        self.dismiss()