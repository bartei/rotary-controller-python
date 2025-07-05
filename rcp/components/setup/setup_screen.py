import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen
# from kivy.factory import Factory

# Those are needed for the Factory class
# from rcp.components.setup.scale_panel import ScalePanel
# from rcp.components.setup.network_panel import NetworkPanel
# from rcp.components.setup.formats_panel import FormatsPanel
# from rcp.components.setup.servo_panel import ServoPanel


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class SetupScreen(Screen):
    pass
    # def __init__(self, **kw):
    #     from kivy.app import App
    #     self.app = App.get_running_app()
    #     super().__init__(**kw)

    # def scale_panel(self, scale):
    #     self.dismiss()
    #     Factory.ScalePanel(scale=scale).open()
    #
    # def network_panel(self):
    #     self.dismiss()
    #     Factory.NetworkPanel().open()
    #
    # def formats_panel(self):
    #     self.dismiss()
    #     Factory.FormatsPanel(formats=self.app.formats).open()
    #
    # def servo_panel(self):
    #     self.dismiss()
    #     Factory.ServoPanel(servo=self.app.servo).open()