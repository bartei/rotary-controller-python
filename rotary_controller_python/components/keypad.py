import os
from kivy.logger import Logger
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

    def show(self, container, set_method):
        self.set_method = set_method
        self.container = container
        self.open()

    def confirm(self):
        try:
            value = self.ids['value'].text
            if "." in value:
                value = float(value)
            else:
                value = int(value)

            setattr(self.container, self.set_method, value)
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self):
        # if self.old_value is not None:
        #     self.ids['value'].text = "{:+0.4f}".format(self.old_value)
        self.dismiss()

    def dot_key(self, *args):
        if "." not in self.ids['value'].text:
            self.ids['value'].text += "."

    def sign_key(self, *args):
        if self.ids['value'].text[0:1] == "-":
            self.ids['value'].text = self.ids['value'].text[1:]
        else:
            self.ids['value'].text = "-" + self.ids['value'].text
