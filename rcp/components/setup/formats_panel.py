import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class FormatsPanel(BoxLayout):
    formats = ObjectProperty()
    stored_volume = None  # Store the volume level before muting

    def __init__(self, formats, **kv):
        self.formats = formats
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))
        
    def toggle_mute(self):
        """Toggle between muted and unmuted states"""
        if self.formats.volume > 0:
            # We're unmuted, so store the current volume and mute
            self.stored_volume = self.formats.volume
            self.formats.volume = 0
            self.ids.volume_slider.value = 0
        else:
            # We're muted, so restore the previous volume
            if self.stored_volume is not None and self.stored_volume > 0:
                self.formats.volume = self.stored_volume
                self.ids.volume_slider.value = self.stored_volume
            else:
                # If we don't have a stored volume or it's 0, set to default
                self.formats.volume = 0.2
                self.ids.volume_slider.value = 0.2
