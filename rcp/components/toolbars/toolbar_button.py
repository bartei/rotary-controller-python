import os
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.lang import Builder

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ToolbarButton(Button):
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