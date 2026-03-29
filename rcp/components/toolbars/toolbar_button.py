from kivy.logger import Logger
from kivy.uix.button import Button

from rcp.components.widgets.beep_mixin import BeepMixin
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ToolbarButton(BeepMixin, Button):
    pass
    # font_name = StringProperty("fonts/Manrope-Bold.ttf")
    # font_size = NumericProperty(36)
    #
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.size_hint = (None, None)
        # self.bind(width=self.update_height) # Bind width to update_height
        # self.update_height(self, self.width)

    # def update_height(self, instance, value):
    #     self.height = self.width