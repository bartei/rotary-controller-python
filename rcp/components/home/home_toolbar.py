from kivy.app import App
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from rcp.components.toolbars.toolbar_button import ToolbarButton
from rcp.components.keypad import Keypad
from rcp.components.plot.scene_popup import ScenePopup
from rcp.components.setup.setup_popup import SetupPopup
from rcp.components.home.mode_popup import ModePopup

log = Logger.getChild(__name__)


class HomeToolbar(BoxLayout):
    def __init__(self, **kv):
        self.app = App.get_running_app()
        super(HomeToolbar, self).__init__(**kv)
        self.size_hint_x = None
        self.size_hint_y = 1
        self.width = 80
        self.orientation = "vertical"

        # Current Format Button
        current_format = ToolbarButton(
            text = "",
            on_release=self.app.formats.toggle
        )
        def update_current_format(*_):
            current_format.text = self.app.formats.current_format
        update_current_format()
        self.app.formats.bind(current_format=update_current_format)
        self.add_widget(current_format)

        # Current Offset Button
        def keypad_current_offset(*_):
            keypad = Keypad()
            keypad.show(self.app, 'currentOffset')

        current_offset = ToolbarButton(
            text = "",
            on_release=keypad_current_offset
        )
        def update_current_offset(*_):
            current_offset.text = "P{:d}".format(self.app.currentOffset)
        update_current_offset()
        self.app.bind(currentOffset=update_current_offset)
        self.add_widget(current_offset)

        # Magic Wand Button
        def popup_scene(*_):
            ScenePopup().open()
        magic_wand = ToolbarButton(
            font_name="fonts/Font Awesome 6 Free-Solid-900.otf",
            text="\ue2ca",
            on_release=popup_scene
        )
        self.add_widget(magic_wand)

        # Mode Button
        def update_current_mode(*_):
            if self.app.current_mode == 1:
                mode_button.text = "IDX"
            if self.app.current_mode == 2:
                mode_button.text = "ELS"
            if self.app.current_mode == 3:
                mode_button.text = "JOG"

        def popup_mode(*_):
            ModePopup().show_with_callback(self.app.set_mode, self.app.current_mode)
        mode_button = ToolbarButton(
            text="IDX",
            on_release=popup_mode
        )
        self.app.bind(current_mode=update_current_mode)
        self.add_widget(mode_button)

        # Setup Button
        def popup_setup(*_):
            SetupPopup().open()
        setup = ToolbarButton(
            font_name="fonts/Font Awesome 6 Free-Solid-900.otf",
            text="\uf085",
            on_release=popup_setup
        )
        self.add_widget(setup)

        self.add_widget(Widget())
