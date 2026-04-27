from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.components.popups.mode_popup import ModePopup
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class HomeToolbar(BoxLayout):
    current_mode_desc = StringProperty("IDX")

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self._wizard_btn = None
        super(HomeToolbar, self).__init__(**kv)
        self.app.bind(current_mode=self.update_current_mode)
        self.update_current_mode(None, self.app.current_mode)
        self.app.formats.bind(show_wizard=self._toggle_wizard)
        Clock.schedule_once(self._init_wizard)

    def _init_wizard(self, *args):
        self._wizard_btn = self.ids.get('wizard_button')
        if not self.app.formats.show_wizard:
            self._toggle_wizard(None, False)

    def _toggle_wizard(self, instance, value):
        if self._wizard_btn is None:
            return
        if value and self._wizard_btn.parent is None:
            self.add_widget(self._wizard_btn, index=len(self.children) - 3)
        elif not value and self._wizard_btn.parent is not None:
            self.remove_widget(self._wizard_btn)

    # def popup_scene(self, *_):
    #     ScenePopup().open()

    def update_current_mode(self, instance, value):
        if self.app.current_mode == 1:
            self.current_mode_desc = "IDX"
        if self.app.current_mode == 2:
            self.current_mode_desc = "ELS"
        if self.app.current_mode == 3:
            self.current_mode_desc = "JOG"
        if self.app.current_mode == 4:
            self.current_mode_desc = "DRO"
        if self.app.current_mode == 5:
            self.current_mode_desc = "AT"

    def popup_mode(self, *_):
        ModePopup().show_with_callback(self.app.set_mode, self.app.current_mode)
