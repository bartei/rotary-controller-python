import os
from tkinter import Label

from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)

class JogBar(BoxLayout):
    desired_speed = NumericProperty(0)
    enable_jog = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        super().__init__(**kwargs)
        self.bind(desired_speed=self.update_jog)
        self.bind(enable_jog=self.update_jog)

    def update_jog(self, instance, value):
        if self.desired_speed > self.app.servo.maxSpeed:
            self.desired_speed = self.app.servo.maxSpeed
        if self.desired_speed < -self.app.servo.maxSpeed:
            self.desired_speed = -self.app.servo.maxSpeed

        if self.enable_jog:
            self.app.servo.jogSpeed = self.desired_speed
            self.app.servo.servoEnable = 2
        else:
            self.app.servo.jogSpeed = 0
            # self.app.servo.servoEnable = 0
