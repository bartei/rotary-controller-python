import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.popup import Popup


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class JogPopup(Popup):
    desired_speed = NumericProperty(0)
    enable_jog = BooleanProperty(False)

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(*kv)
        self.app.bind(update_tick=self.update_tick)

    def update_tick(self, *args, **kv):
        if self.enable_jog:
            self.app.servo.jogSpeed = self.desired_speed
            self.app.servo.servoEnable = 2
        else:
            self.app.servo.jogSpeed = 0

    def update_desired_speed(self, *args, **kv):
        value = args[1]
        self.desired_speed = value

    def on_dismiss(self):
        self.app.servo.jogSpeed = 0
        self.app.servo.servoEnable = 0
        log.info("Close jog page")
