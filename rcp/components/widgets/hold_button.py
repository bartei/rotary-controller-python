import os

from kivy.logger import Logger
from kivy.uix.button import Button

log = Logger.getChild(__name__)

#Hold button created to keep tracking of press state even if cursor leaves button area
class HoldButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_pressed = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._is_pressed = True
            self.dispatch('on_press')
            # Grab the touch to keep receiving its events even if cursor leaves
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # Ensure we get the release even if outside button
            self._is_pressed = False
            self.dispatch('on_release')
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)
