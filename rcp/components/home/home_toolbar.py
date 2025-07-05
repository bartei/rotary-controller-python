import os

from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

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

    # def popup_scene(self, *_):
    #     ScenePopup().open()

    def update_current_mode(self, instance, value):
        if self.app.current_mode == 1:
            self.current_mode_desc = "IDX"
        if self.app.current_mode == 2:
            self.current_mode_desc = "ELS"
        if self.app.current_mode == 3:
            self.current_mode_desc = "JOG"

    def popup_mode(self, *_):
        ModePopup().show_with_callback(self.app.set_mode, self.app.current_mode)
