import os

from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder

from rcp.components.toolbars.toolbar_button import ToolbarButton
from rcp.components.keypad import Keypad
from rcp.components.plot.scene_popup import ScenePopup
from rcp.components.setup.setup_popup import SetupPopup
from rcp.components.home.mode_popup import ModePopup

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

class HomeToolbar(BoxLayout):
    current_mode_desc = StringProperty("IDX")

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super(HomeToolbar, self).__init__(**kv)
        self.app.bind(current_mode=self.update_current_mode)

        # Current Format Button
        # current_format = ToolbarButton(
        #     text = "",
        #     width = self.width,
        #     on_release=self.app.formats.toggle,
        # )
        # def update_current_format(*_):
        #     current_format.text = self.app.formats.current_format
        # update_current_format()
        # self.app.formats.bind(current_format=update_current_format)
        # self.add_widget(current_format)

        # Current Offset Button
        # def keypad_current_offset(*_):
        #     keypad = Keypad()
        #     keypad.show(self.app, 'currentOffset')
        #
        # current_offset = ToolbarButton(
        #     text = "",
        #     width = self.width,
        #     on_release=keypad_current_offset
        # )
        # def update_current_offset(*_):
        #     current_offset.text = "P{:d}".format(self.app.currentOffset)
        # update_current_offset()
        # self.app.bind(currentOffset=update_current_offset)
        # self.add_widget(current_offset)

        # Magic Wand Button
        # def popup_scene(*_):
        #     ScenePopup().open()
        # magic_wand = ToolbarButton(
        #     font_name="fonts/Font Awesome 6 Free-Solid-900.otf",
        #     text="\ue2ca",
        #     width = self.width,
        #     on_release=popup_scene,
        # )
        # self.add_widget(magic_wand)

        # Mode Button
        # def update_current_mode(*_):
        #     if self.app.current_mode == 1:
        #         mode_button.text = "IDX"
        #     if self.app.current_mode == 2:
        #         mode_button.text = "ELS"
        #     if self.app.current_mode == 3:
        #         mode_button.text = "JOG"

        # def popup_mode(*_):
        #     ModePopup().show_with_callback(self.app.set_mode, self.app.current_mode)
        # mode_button = ToolbarButton(
        #     text="IDX",
        #     width = self.width,
        #     on_release=popup_mode
        # )
        # # update_current_mode()
        # self.app.bind(current_mode=update_current_mode)
        # self.add_widget(mode_button)

        # Setup Button
        # def popup_setup(*_):
        #     SetupPopup().open()
        # setup = ToolbarButton(
        #     font_name="fonts/Font Awesome 6 Free-Solid-900.otf",
        #     text="\uf085",
        #     width = self.width,
        #     on_release=popup_setup
        # )
        # self.add_widget(setup)
        # self.add_widget(Widget())

    def popup_scene(self, *_):
        ScenePopup().open()

    def update_current_mode(self, instance, value):
        if self.app.current_mode == 1:
            self.current_mode_desc = "IDX"
        if self.app.current_mode == 2:
            self.current_mode_desc = "ELS"
        if self.app.current_mode == 3:
            self.current_mode_desc = "JOG"

    def popup_mode(self, *_):
        ModePopup().show_with_callback(self.app.set_mode, self.app.current_mode)

    def popup_setup(self, *_):
        SetupPopup().open()