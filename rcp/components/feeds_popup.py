import os

from kivy.lang import Builder
from kivy.app import App
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

class KeypadButton(Button):
    merda = NumericProperty(0)

class FeedsPopup(Popup):
    set_method = None
    container = None

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        super().__init__(**kwargs)
        self.title = f"Select Feed Mode"
        self.size_hint = (0.8, 0.3)
        self.auto_dismiss = False

        layout = BoxLayout(orientation="vertical")

        row1 = BoxLayout(orientation="horizontal")
        row1.add_widget(KeypadButton(
            text="Thread\nIN",on_release=self.confirm,background_color=[1, 1, 1, 1], merda=1)
        )
        row1.add_widget(KeypadButton(
            text="Thread\nMM",on_release=self.confirm,background_color=[1, 1, 1, 1], merda=2)
        )
        row1.add_widget(KeypadButton(
            text="Feed\nIN",on_release=self.confirm,background_color=[1, 1, 1, 1], merda=3)
        )
        row1.add_widget(KeypadButton(
            text="Feed\nMM",on_release=self.confirm,background_color=[1, 1, 1, 1], merda=4)
        )
        row1.add_widget(KeypadButton(
            text="Return",on_release=self.cancel,background_color=[1, 0, 0, 1])
        )
        layout.add_widget(row1)

        self.add_widget(layout)
        self.callback_fn = None
        self.current_value = None


    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)


    def show_with_callback(self, callback_fn, current_value=None):
        if current_value is not None:
            # Use the specified current value if passed
            self.current_value = float(current_value)

        self.callback_fn = callback_fn
        self.set_method = None
        self.container = None
        self.open()

    def confirm(self, instance: KeypadButton):
        try:
            value = instance.merda
            self.callback_fn(value)
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self, *args, **kwargs):
        self.dismiss()

