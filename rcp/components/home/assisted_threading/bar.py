from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

from rcp import feeds
from rcp.components.widgets.custom_popup import CustomPopup
from rcp.components.widgets.hold_button import HoldButton
from rcp.components.home.assisted_threading.wizard import AssistedThreadingWizard
from rcp.components.home.assisted_threading.thread_type import ThreadType
from rcp.dispatchers.saving_dispatcher import SavingDispatcher
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)

load_kv(__file__)

class AssistedThreadingBar(BoxLayout, SavingDispatcher):
    # ── Per-job thread settings (saved on the bar) ────────────────────
    metric_mode = BooleanProperty(True)  # This is for the actual threading logic
    selected_pitch = StringProperty("")
    current_feeds_index = NumericProperty(0)
    thread_profile_type = StringProperty("ISO_METRIC")
    shaft_diameter = NumericProperty(1)
    left_hand_thread = BooleanProperty(False)
    inner_thread = BooleanProperty(False)

    compound_infeed_mode = BooleanProperty(False)
    compound_infeed_offset_degrees = NumericProperty(1.0)

    is_running = BooleanProperty(False)
    action_button_enabled = BooleanProperty(True)
    label_text = StringProperty("")
    display_value = StringProperty("")
    next_button_text = StringProperty("")
    start_position = NumericProperty(0)
    stop_position = NumericProperty(0)
    material_width = NumericProperty(0)
    cutting_depth = NumericProperty(0)
    last_cutting_depth = NumericProperty(0)
    retract_button_visible = BooleanProperty(False)
    retract_button_enabled = BooleanProperty(True)
    _skip_save = [
        "is_running",
        "action_button_enabled",
        "label_text",
        "display_value",
        "start_position",
        "stop_position",
        "material_width",
        "cutting_depth",
        "last_cutting_depth",
        "retract_button_visible",
        "retract_button_enabled"
    ]

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self.action_button_condition_fn = None
        self.retract_button_condition_fn = None
        super().__init__(**kv)

        self.current_feeds_table = feeds.table["Thread MM"] if self.metric_mode else feeds.table["Thread IN"]
        self.update_feeds_ratio(self, None)

        # Initialize with default thread type if not set
        if not self.thread_profile_type:
            self.thread_profile_type = ThreadType.ISO_METRIC.value
        self.wizard = AssistedThreadingWizard(self)

        self.app.bind(current_mode=self.on_mode_change)
        self.bind(left_hand_thread=self.update_feeds_ratio)

    def toggle_is_running(self):
        if not self.is_running:
            missing = []
            if self.app.els.get_spindle_axis() is None:
                missing.append("Spindle")
            if self.app.els.get_z_axis() is None:
                missing.append("Saddle (Z)")
            if self.app.els.get_x_axis() is None:
                missing.append("Cross-slide (X)")
            if missing:
                CustomPopup(
                    title="Axes Not Configured",
                    message=f"The following axes are not set in ELS: {', '.join(missing)}. Please configure them in Settings.",
                    button_text="OK",
                ).open()
                return
        self.is_running = not self.is_running
        if self.is_running:
            self.wizard.start()
        else:
            self.stop_wizard()

    def stop_wizard(self):
            self.wizard.stop()

    def on_metric_mode(self, instance, value):
        self.current_feeds_table = feeds.table["Thread MM"] if value else feeds.table["Thread IN"]

    def on_mode_change(self, instance, mode):
        if mode == 5: # AT mode
            self.update_feeds_ratio(None, None)

    def on_retract_button_pressed(self):
        """Called when the retract button is pressed."""
        if not self.retract_button_enabled:
            return
        self.wizard.start_retracting()

    def on_retract_button_released(self):
        """Called when the retract button is released."""
        if not self.retract_button_enabled:
            return
        self.wizard.stop_retracting()

    def on_action_button_clicked(self):
        """Called when the right button is pressed."""
        if self.is_running:
            self.wizard.goto_next_step()
        else:
            self.open_settings()

    def update_feeds_ratio(self, instance, value):
        if self.app.current_mode != 5:
            return  # only sync in AT mode

        ratio = self.current_feeds_table[self.current_feeds_index].ratio
        spindle_axis = self.app.els.get_spindle_axis()
        if spindle_axis is not None:
            direction = -1 if self.left_hand_thread else 1
            spindle_axis.syncRatioNum = ratio.numerator * direction
            spindle_axis.syncRatioDen = ratio.denominator
        log.info(f"Configured ratio is: {ratio.numerator}/{ratio.denominator}, left_hand_thread={self.left_hand_thread}")

    def open_settings(self):
        from rcp.components.home.assisted_threading.settings_popup import AssistedThreadingSettingsPopup
        popup = AssistedThreadingSettingsPopup(assistedThreadingBar=self)
        popup.open()

    def bind_display_value_to_scale(self, axis):
        """Bind display_value to an AxisDispatcher's formattedPosition with strict keypad override support."""

        # Unbind any previous bindings
        self.unbind_all_display_value()

        # Store the axis (AxisDispatcher) for later unbind
        self._bound_scale = axis
        inp = axis._primary_input() if axis is not None else None

        # --- Encoder update handler (fires on raw encoder tick) ---
        def on_encoder_update(*_):
            # Cancel manual override if the encoder moves
            if self.wizard and self.wizard.manual_stop_length is not None:
                log.info("Scale encoder moved — discarding manual stop length override")
                self.wizard.manual_stop_length = None
            # Display the axis formatted position (not raw encoder ticks)
            self.display_value = axis.formattedPosition
            self.update_buttons_state()

        # --- Format update handler ---
        def on_format_update(instance, value):
            # Only update display if NOT in manual override
            if not (self.wizard and self.wizard.manual_stop_length is not None):
                self.display_value = value

        # Keep references so we can unbind later
        self._on_encoder_update = on_encoder_update
        self._on_format_update = on_format_update

        # encoderCurrent lives on InputDispatcher; formattedPosition on AxisDispatcher
        if inp is not None:
            inp.bind(encoderCurrent=on_encoder_update)
        axis.bind(formattedPosition=on_format_update)

        # Initial display
        self.display_value = axis.formattedPosition

    def bind_display_value_to_servo_position(self):
        """Bind display_value to the servo's formattedPosition."""
        # Unbind any previous bindings
        self.unbind_all_display_value()
        self._bound_servo = self.app.servo

        def on_servo_position_update(instance, value):
            self.display_value = value

        self._on_servo_position_update = on_servo_position_update

         # Bind to servo's formattedPosition
        self.app.servo.bind(formattedPosition=on_servo_position_update)

    def bind_btn_value_on_release(self, on_release_fn):
        """Bind the value button to a function."""
         # Unbind old function if it exists
        if hasattr(self, "_on_value_button_release") and self._on_value_button_release is not None:
            self.ids.btn_value.unbind(on_release=self._on_value_button_release)

        # Store the binding function
        self._on_value_button_release = on_release_fn

        if(on_release_fn is None):
            # If None is passed, disable the button
            self.ids.btn_value.disabled = True
            return

        self.ids.btn_value.disabled = False
        # Bind the new function
        self.ids.btn_value.bind(on_release=on_release_fn)

    def unbind_all_display_value(self):
        if hasattr(self, "_bound_scale") and self._bound_scale is not None:
            inp = self._bound_scale._primary_input()
            if inp is not None:
                inp.unbind(encoderCurrent=self._on_encoder_update)
            self._bound_scale.unbind(formattedPosition=self._on_format_update)
            self._bound_scale = None
        if hasattr(self, "_bound_servo") and self._bound_servo is not None:
            self._bound_servo.unbind(formattedPosition=self._on_servo_position_update)
            self._bound_servo = None
        # Unbind threading progress display if it was bound
        if hasattr(self.wizard, "_progress_display_scale") and self.wizard._progress_display_scale is not None:
            if hasattr(self.wizard, "_on_threading_progress_update"):
                self.wizard._progress_display_scale.unbind(encoderCurrent=self.wizard._on_threading_progress_update)
            self.wizard._progress_display_scale = None

    def update_buttons_state(self):
        """Evaluate whether the action/retract buttons should be enabled."""
        if self.action_button_condition_fn:
            self.action_button_enabled = self.action_button_condition_fn()
        else:
            self.action_button_enabled = True

        if self.retract_button_condition_fn:
            self.retract_button_enabled = self.retract_button_condition_fn()
        else:
            self.retract_button_enabled = True
