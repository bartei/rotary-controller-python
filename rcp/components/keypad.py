from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from rcp.components.toolbars.keypad_button import KeypadButton
from rcp.components.toolbars.keypad_icon_button import KeypadIconButton

log = Logger.getChild(__name__)


class Keypad(Popup):
    set_method = None
    container = None
    current_value = NumericProperty(0)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        self.title = f"Old Value: {self.current_value}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        layout = BoxLayout(orientation="vertical")

        # Label to display the value
        value_label = Label(
            font_name="fonts/Manrope-Bold.ttf",
            font_size=48
        )
        self.ids['value'] = value_label
        layout.add_widget(value_label)

        row1 = BoxLayout(orientation="horizontal")
        row1.add_widget(KeypadButton(text="7",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row1.add_widget(KeypadButton(text="8",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row1.add_widget(KeypadButton(text="9",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row1.add_widget(KeypadIconButton(text="\uf55a",on_release=self.delete_text,background_color=[1, 1, 1, 1]))
        layout.add_widget(row1)

        row2 = BoxLayout(orientation="horizontal")
        row2.add_widget(KeypadButton(text="4",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row2.add_widget(KeypadButton(text="5",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row2.add_widget(KeypadButton(text="6",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row2.add_widget(KeypadButton(text="1/2",on_release=self.halve_value))
        layout.add_widget(row2)

        row3 = BoxLayout(orientation="horizontal")
        row3.add_widget(KeypadButton(text="1",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row3.add_widget(KeypadButton(text="2",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row3.add_widget(KeypadButton(text="3",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row3.add_widget(KeypadIconButton(text="\ue43c",on_release=self.sign_key,background_color=[1, 1, 1, 1]))
        layout.add_widget(row3)

        row4 = BoxLayout(orientation="horizontal")
        row4.add_widget(KeypadButton(text="0",on_release=self.add_text,background_color=[1, 1, 1, 1]))
        row4.add_widget(KeypadButton(text=".",on_release=self.dot_key,background_color=[1, 1, 1, 1]))
        row4.add_widget(KeypadIconButton(text="\uf00d",on_release=self.cancel,background_color=self.app.formats.cancel_color))
        row4.add_widget(KeypadIconButton(text="\uf00c",on_release=self.confirm,background_color=self.app.formats.accept_color))
        layout.add_widget(row4)

        self.add_widget(layout)
        # Bind the keyboard to this widget
        self._keyboard = Window._system_keyboard
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.callback_fn = None

    def on_current_value(self, instance, value):
        self.title = f"Old Value: {value}"

    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)

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
            # Use the specified current value if passed
            self.current_value = float(current_value)
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

    def show_with_callback(self, callback_fn, current_value=None):
        if current_value is not None:
            # Use the specified current value if passed
            self.current_value = float(current_value)

        self.callback_fn = callback_fn
        self.set_method = None
        self.container = None
        self.open()

    def confirm(self, *args, **kwargs):
        try:
            value = self.ids['value'].text
            if type(value) is str and "." in value:
                value = float(value)
            else:
                value = int(value)

            if self.callback_fn is not None:
                self.callback_fn(value)
            else:
                setattr(self.container, self.set_method, value)

            self._keyboard.release()
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self, *args, **kwargs):
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

    def add_text(self, button):
        self.ids['value'].text += button.text

    def delete_text(self, button):
        self.ids['value'].text = self.ids['value'].text[:-1]

    def halve_value(self, button):
        self.ids['value'].text = str(self.current_value / 2)
