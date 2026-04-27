from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from rcp.components.home.assisted_threading.thread_type import ThreadType
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)

load_kv(__file__)


class AssistedThreadingSettingsPopup(Popup):
    assistedThreadingBar = ObjectProperty(None)

    def __init__(self, **kv):
        super().__init__(**kv)

    def get_pitches(self):
        if not self.assistedThreadingBar:
            return []

        return [f.name for f in self.assistedThreadingBar.current_feeds_table]

    def get_thread_types(self):
        """Get available thread types based on metric mode."""
        if self.assistedThreadingBar.metric_mode:
            return [ThreadType.ISO_METRIC.value, ThreadType.ACME.value]
        else:
            return [ThreadType.UNIFIED.value, ThreadType.WHITWORTH.value, ThreadType.ACME.value]

    def on_metric_mode_changed(self, value):
        self.assistedThreadingBar.metric_mode = value
        pitches_dropdown = self.ids.pitches_dropdown
        pitches = self.get_pitches()
        pitches_dropdown.options = pitches
        first_pitch = pitches[0] if pitches else ""
        pitches_dropdown.value = first_pitch
        self.on_pitch_selected(0, first_pitch)

        # Update thread type options based on metric mode
        thread_type_dropdown = self.ids.thread_type_dropdown
        thread_type_dropdown.options = self.get_thread_types()
        # Reset to first available type
        first_type = self.get_thread_types()[0] if self.get_thread_types() else ThreadType.ISO_METRIC.value
        thread_type_dropdown.value = first_type
        self.assistedThreadingBar.thread_profile_type = ThreadType(first_type).value

        log.info(f"Metric mode changed to: {value}")

    def on_pitch_selected(self, index, selected_pitch):
        self.assistedThreadingBar.selected_pitch = selected_pitch
        self.assistedThreadingBar.current_feeds_index = index
        self.assistedThreadingBar.update_feeds_ratio(None,None)
        log.info(f"Selected pitch: {selected_pitch}")

    def on_thread_type_selected(self, value):
        """Handle thread type selection."""
        try:
            # Convert string value back to ThreadType enum
            thread_type = ThreadType(value)
            self.assistedThreadingBar.thread_profile_type = thread_type.value
            log.info(f"Selected thread type: {thread_type}")
        except ValueError:
            log.warning(f"Invalid thread type value: {value}")

    def on_compound_infeed_mode_changed(self, value):
        self.assistedThreadingBar.compound_infeed_mode = value
        log.info(f"Compound infeed mode changed to: {value}")
