from kivy.app import App
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from rcp.components.toolbars.keypad_button import KeypadButton

log = Logger.getChild(__name__)


class ModePopup(Popup):
    current_value = NumericProperty(1)

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        super().__init__(**kwargs)
        self.title = f"Select Mode"
        self.size_hint = (0.6, 0.8)
        self.auto_dismiss = False

        buttons = BoxLayout(orientation="vertical")
        buttons.add_widget(KeypadButton(text="Indexing", return_value=1, on_release=self.confirm))
        buttons.add_widget(KeypadButton(text="ELS", return_value=2, on_release=self.confirm))
        buttons.add_widget(KeypadButton(text="JOG", return_value=3, on_release=self.confirm))
        self.add_widget(buttons)
        self.callback_fn = None

    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)

    def show_with_callback(self, callback_fn, current_value=None):
        if current_value is not None:
            # Use the specified current value if passed
            self.current_value = float(current_value)

        self.callback_fn = callback_fn
        self.open()

    def confirm(self, instance: KeypadButton):
        try:
            value = instance.return_value
            self.callback_fn(value)
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self, *args, **kwargs):
        self.dismiss()
