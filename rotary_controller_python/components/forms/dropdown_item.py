import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class DropDownItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty(False)
    options = ListProperty([])
    dropdown = ObjectProperty()
    main_button: Button = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.dropdown = DropDown()
        self._options = []
        self.dropdown.bind(on_select=lambda instance, x: setattr(self, 'value', x))

    def delete_all_dropdown_options(self):
        for item in self._options:
            self.dropdown.remove_widget(item)

    def on_value(self, instance, value):
        self.main_button.text = value

    def on_options(self, instance, value):
        # Clean any existing
        self.delete_all_dropdown_options()

        for item in self.options:
            btn = Button(text=item, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
            self._options.append(btn)
