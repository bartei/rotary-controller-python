import os
import logging

from kivy.uix.popup import Popup
from kivy.lang import Builder

log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Keypad(Popup):
    reference = None
    old_value = None

    def show(self, reference):
        self.title += "{:+0.4f}".format(getattr(reference.args[0], reference.args[1]))
        self.old_value = getattr(reference.args[0], reference.args[1])
        self.ids['value'].bind(text=reference)
        self.open()

    def confirm(self):
        self.dismiss()

    def cancel(self):
        if self.old_value is not None:
            self.ids['value'].text = "{:+0.4f}".format(self.old_value)
        self.dismiss()

    def dot_key(self, *args):
        if "." not in self.ids['value'].text:
            self.ids['value'].text += "."

    def sign_key(self, *args):
        if self.ids['value'].text[0:1] == "-":
            self.ids['value'].text = self.ids['value'].text[1:]
        else:
            self.ids['value'].text = "-" + self.ids['value'].text
