import os

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Keypad(Popup):
    set_method = None
    container = None
    current_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind the keyboard to this widget
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(f'Keycode: {keycode}, text: {text}, modifiers: {modifiers}')
        # # Update the label to show which key was pressed
        # log.info(f'Last key pressed: {text}')
        if text == ".":
            self.dot_key()
        if text == "-":
            self.sign_key()
        if text in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            self.ids['value'].text += text
        if keycode[1] == "backspace":
            self.ids['value'].text = self.ids['value'].text[:-1]
        if keycode[1] == "escape":
            self.cancel()
        if keycode[1] == "enter":
            self.confirm()

        return True  # Return True to accept the key. False would reject the key press.

    def show(self, container, set_method, current_value=None):
        if current_value is not None:
            ## Use the specified current value if passed
            self.current_value = current_value
        else:
            try:
                self.current_value = getattr(container, set_method)
            except Exception as e:
                log.debug(e.__str__())
                pass
            # try to get the current value from the container method specified if
        self.set_method = set_method
        self.container = container
        self.open()

    def confirm(self):
        try:
            value = self.ids['value'].text
            if type(value) is str and "." in value:
                value = float(value)
            else:
                value = int(value)

            setattr(self.container, self.set_method, value)
            self._keyboard.release()
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self):
        self._keyboard.release()
        self.dismiss()

    def dot_key(self, *args):
        if "." not in self.ids['value'].text:
            self.ids['value'].text += "."

    def sign_key(self, *args):
        if self.ids['value'].text[0:1] == "-":
            self.ids['value'].text = self.ids['value'].text[1:]
        else:
            self.ids['value'].text = "-" + self.ids['value'].text
