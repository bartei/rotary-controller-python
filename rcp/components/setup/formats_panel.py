import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout


log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class FormatsPanel(BoxLayout):
    formats = ObjectProperty()
    stored_volume = None  # Store the volume level before muting
    beep_options = ListProperty([
        "beep.mp3",
        "beep-soft.mp3", 
        "beep-low.mp3",
        "beep-chime.mp3", 
        "beep-warm.mp3",
        "beep-click.mp3",
        "beep-double.mp3"
    ])

    def __init__(self, formats, **kv):
        self.formats = formats
        
        # Create user-friendly display names for beep options
        self.beep_display_options = [
            "Original",
            "Soft Tone", 
            "Low Tone",
            "Chime", 
            "Warm Tone",
            "Quick Click",
            "Double Beep"
        ]
        
        # Create mapping between display names and file names
        self.beep_file_mapping = dict(zip(self.beep_display_options, self.beep_options))
        self.beep_display_mapping = dict(zip(self.beep_options, self.beep_display_options))
        
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))
        
    def get_display_name(self, filename):
        """Get user-friendly display name for a beep file"""
        return self.beep_display_mapping.get(filename, filename)
        
    def get_filename(self, display_name):
        """Get filename for a display name"""
        return self.beep_file_mapping.get(display_name, display_name)
        
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
