from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from rcp.components.popups.help_popup import HelpPopup  # noqa: F401
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

DROPDOWN_OPTION_COLOR = [0.15, 0.3, 0.55, 1]


class DropDownItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty(False)
    options = ListProperty([])
    help_file = StringProperty("")
    dropdown = ObjectProperty()
    main_button: Button = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.dropdown = DropDown()
        self.dropdown.container.padding = [4, 4, 4, 4]
        self.dropdown.container.spacing = 2
        with self.dropdown.canvas.before:
            Color(0, 0, 0, 0.9)
            self._bg_rect = Rectangle()
        self.dropdown.bind(pos=self._update_bg, size=self._update_bg)
        self._options = []
        self.dropdown.bind(on_select=lambda instance, x: setattr(self, 'value', x))

    def _update_bg(self, *args):
        self._bg_rect.pos = self.dropdown.pos
        self._bg_rect.size = self.dropdown.size

    def delete_all_dropdown_options(self):
        for item in self._options:
            self.dropdown.remove_widget(item)

    def on_value(self, instance, value):
        self.main_button.text = value

    def on_options(self, instance, value):
        # Clean any existing
        self.delete_all_dropdown_options()

        from rcp.app import MainApp
        app = MainApp.get_running_app()
        font_size = app.formats.font_size if app else 24

        for item in self.options:
            btn = Button(
                text=item, size_hint_y=None, height=60,
                font_size=font_size, background_color=DROPDOWN_OPTION_COLOR,
            )
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
            self._options.append(btn)
