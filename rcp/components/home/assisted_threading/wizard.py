import logging
from fractions import Fraction

from kivy.logger import Logger

from rcp.components.home.assisted_threading.calculations import AssistedThreadingCalculationsMixin
from rcp.components.home.assisted_threading.motion import AssistedThreadingMotionMixin
from rcp.components.home.assisted_threading.safety import AssistedThreadingSafetyMixin

log = Logger.getChild(__name__)


class AssistedThreadingWizard(
    AssistedThreadingCalculationsMixin,
    AssistedThreadingMotionMixin,
    AssistedThreadingSafetyMixin,
):
    # ---------------------------------------------------------------------------
    # Axis / input accessors
    # ---------------------------------------------------------------------------

    @property
    def saddle_scale(self):
        """Returns the AxisDispatcher for the saddle (Z) axis."""
        return self.app.els.get_z_axis()

    @property
    def cross_slide_scale(self):
        """Returns the AxisDispatcher for the cross-slide (X) axis."""
        return self.app.els.get_x_axis()

    @property
    def saddle_input(self):
        """Returns the InputDispatcher (raw encoder) for the saddle axis."""
        axis = self.saddle_scale
        return axis._primary_input() if axis is not None else None

    @property
    def cross_slide_input(self):
        """Returns the InputDispatcher (raw encoder) for the cross-slide axis."""
        axis = self.cross_slide_scale
        return axis._primary_input() if axis is not None else None

    # ---------------------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------------------

    def __init__(self, bar):
        from rcp.app import MainApp
        log.info("Initializing AssistedThreadingWizard")
        self.bar = bar
        self.app: MainApp = MainApp.get_running_app()
        self.servo = self.app.servo
        self.current_step = 0
        self._threading_started = False
        self._threading_active_confirmed = False
        self._current_callback = None
        self._servo_watch_callback = None
        self.manual_stop_length = None
        self.manual_cutting_depth = None
        self._last_saddle_encoder_value = None
        self._start_position_preloaded = False
        self._steps = [
            self._step_set_initial_position,                # Step 1
            self._step_set_stop_position,                   # Step 2
            self._step_set_material_width_position,         # Step 3
            self._step_set_final_cutting_depth_position,    # Step 4
            self._step_engage_half_nut,                     # Step 5
            self._step_go_to_start,                         # Step 6
            self._step_cut_thread,                          # Step 7
            self._step_depth_reached                        # Step 8
        ]

    def start(self):
        dev = self.app.board.device
        dev['assistedThreadingData']['spindlePhaseTolerance'] = self.app.els.at_rotary_encoder_sync_tolerance

        spindle_axis = self.app.els.get_spindle_axis()
        if spindle_axis is not None:
            inp = spindle_axis._primary_input()
            if inp is not None:
                dev['assistedThreadingData']['spindleCountsPerRev'] = int(spindle_axis._steps_per_revolution())
                dev['assistedThreadingData']['spindleScaleIndex'] = inp.inputIndex

        self.goto_step(0)

    def stop(self):
        # Reset wizard_area to default content
        log.info("Wizard finished")
        self._current_callback = None
        self._threading_started = False
        self._threading_active_confirmed = False
        self.bar.label_text = ""
        self.bar.display_value = ""
        self.bar.action_button_enabled = True
        self.bar.action_button_condition_fn = None
        self.bar.is_running = False
        self.bar.retract_button_visible = False
        self._clear_bar_display()
        self._reset_servo_watch_callback()
        self._reset_encoder_stability_check()

        if self.app.board.connected:
            self.app.board.device['assistedThreadingData']['threadReset'] = 1
            self._stop_servo()

    def goto_step(self, index):
        self.current_step = index
        if 0 <= index < len(self._steps):
            self._steps[index]()
        else:
            self.stop()

    def goto_next_step(self, *args):
        # call the callback; it may return False to tell us "do not auto-advance"
        result = None
        if self._current_callback:
            result = self._current_callback(*args)

        # If callback returned exactly False => callback will handle advancement later
        if result is False:
            return

        if self.bar.is_running:  # check to ensure still running and we didn't stop in the callback
            self.goto_step(self.current_step + 1)

    # ---------------------------------------------------------------------------
    # Instruction / UI setup
    # ---------------------------------------------------------------------------

    def set_instruction(self, label_text, next_button_text, next_button_callback, value_button_fn=None, action_button_condition_fn=None, retract_button_visible=False, retract_button_condition_fn=None):
        self.bar.label_text = label_text
        self.bar.next_button_text = next_button_text
        self._current_callback = next_button_callback
        self.bar.bind_btn_value_on_release(value_button_fn)
        self.bar.action_button_condition_fn = action_button_condition_fn
        self.bar.retract_button_visible = retract_button_visible
        self.bar.retract_button_condition_fn = retract_button_condition_fn

    # ---------------------------------------------------------------------------
    # Retract control
    # ---------------------------------------------------------------------------

    def start_retracting(self):
        log.info("Retract button pressed")
        self.bar.action_button_enabled = False  # disable action button while retracting

        if not self.app.board.connected:
            return
        self.bar.bind_display_value_to_servo_position()  # bind to servo position
        servo_direction = 1 if self.servo.ratioNum * self.servo.ratioDen > 0 else -1
        self.servo.jogSpeed = - servo_direction * self.app.els.at_reversing_speed  # set to reversing speed
        self._apply_reversing_adjusting_acceleration()
        self.servo.set_max_speed(self.app.els.at_reversing_speed)  # ensure step rate supports jog speed
        self.servo.servoEnable = 2

    def stop_retracting(self):
        log.info("Retract button released")
        self.bar.action_button_enabled = True  # re-enable action button
        self.bar.bind_display_value_to_scale(self.cross_slide_scale)
        self.bar.update_buttons_state()

        if not self.app.board.connected:
            return
        self.servo.jogSpeed = 0

        self._servo_watch_callback = self._watch_retracting_stopped
        self.app.board.bind(update_tick=self._servo_watch_callback)

    # ---------------------------------------------------------------------------
    # Step definitions
    # ---------------------------------------------------------------------------

    # Step 1
    def _step_set_initial_position(self):
        self.set_instruction("Go to initial Z and press Set", "Set", self._capture_initial_position)
        self.bar.bind_display_value_to_scale(self.saddle_scale)

    # Step 2
    def _step_set_stop_position(self):
        self.bar.action_button_enabled = False  # Disable until valid
        self.set_instruction("Go to or input stop Z and press Set", "Set", self._capture_stop_position, self._open_stop_position_keypad, self._is_valid_stop_position)
        self.bar.bind_display_value_to_scale(self.saddle_scale)

    # Step 3
    def _step_set_material_width_position(self):
        self.set_instruction("Go to material width and press Set", "Set", self._capture_material_width_position)
        self.bar.bind_display_value_to_scale(self.cross_slide_scale)

    # Step 4
    def _step_set_final_cutting_depth_position(self):
        self._clear_bar_display()

        # Calculate thread depth and show immediately
        calculated_depth = self._calculate_thread_depth()
        self.manual_cutting_depth = None  # Reset manual override
        if calculated_depth is not None:
            is_metric = self.app.formats.current_format == "MM"
            self.bar.display_value = f"{calculated_depth:.3f}" if is_metric else f"{calculated_depth:.4f}"
        else:
            self.bar.display_value = ""

        self.set_instruction(
            "Enter Final Cutting Depth (auto-calculated shown, tap to override)",
            "Set",
            self._capture_final_cutting_depth_position,
            self._open_final_cutting_depth_position_keypad
        )

    # Step 5
    def _step_engage_half_nut(self):
        self.set_instruction("Engage half nut and press Next", "Next", None)
        self._clear_bar_display()

    # Step 6
    def _step_go_to_start(self):
        self.bar.action_button_enabled = False  # Disable until valid
        self.bar.retract_button_enabled = False  # Disable until valid
        self.servo.servoEnable = 1  # Ensure servo enabled
        self.set_instruction("Confirm cross slide retracted and press Go to return to start position", "Go", self._go_to_start, None, self._is_cross_slide_retracted, True, self._is_cross_slide_retracted)
        self.bar.bind_display_value_to_scale(self.cross_slide_scale)
        self.bar.update_buttons_state()

    # Step 7
    def _step_cut_thread(self):
        self.bar.action_button_enabled = False  # Disable until valid
        self.bar.retract_button_enabled = False  # Disable until valid
        self.set_instruction("Go to cutting depth and press Cut to start threading operation", "Cut", self._start_threading_operation, None, None, True)
        self._bind_threading_progress_display()  # Bind to progress display
        self.bar.update_buttons_state()

    # Step 8
    def _step_depth_reached(self):
        self.bar.action_button_enabled = False  # Disable until valid
        self.bar.retract_button_enabled = False  # Disable until valid
        self.set_instruction("Final depth reached. Cut more? Press Stop to quit.", "Cut", self._start_threading_operation, None, None, True)
        self._bind_threading_progress_display()  # Bind to progress display
        self.bar.update_buttons_state()

    # ---------------------------------------------------------------------------
    # Step callbacks
    # ---------------------------------------------------------------------------

    # Step 1
    def _capture_initial_position(self, *args):
        self.bar.start_position = self.saddle_input.encoderCurrent
        self._isStartPositionMetricMode = self.app.formats.current_format == "MM"
        self._startScaledPosition = self.saddle_scale.scaledPosition
        log.info(f"Initial position set to: {self.bar.start_position}")
        return True  # advance to next step

    # Step 2
    def _capture_stop_position(self, *args):
        self.bar.stop_position = self._get_stop_position_units()
        self.manual_stop_length = None  # reset for next run
        log.info(f"Stop position set - (start={self.bar.start_position}, stop={self.bar.stop_position})")
        return True  # advance to next step

    # Step 3
    def _capture_material_width_position(self, *args):
        self.bar.material_width = self.cross_slide_input.encoderCurrent
        self.bar.last_cutting_depth = self.bar.material_width  # Initialize last_cutting_depth to material_width
        self._isMaterialWidthPositionMetricMode = self.app.formats.current_format == "MM"
        self._materialWidthScaledPosition = self.cross_slide_scale.scaledPosition
        log.info(f"Material width set to: {self.bar.material_width}")
        return True  # advance to next step

    # Step 4
    def _capture_final_cutting_depth_position(self, *args):
        # Use manual override if set, otherwise use calculated depth
        is_metric = self.app.formats.current_format == "MM"
        depth = self.manual_cutting_depth if self.manual_cutting_depth is not None else self._calculate_thread_depth()
        encoder_cutting_depth = self._convert_distance_units_to_encoder(self.cross_slide_scale, depth, is_metric)

        self.bar.cutting_depth = self.cross_slide_input.encoderCurrent - (encoder_cutting_depth * self._get_cross_slide_scale_effective_dir())

        log.info(f"Cutting depth set: {depth} (manual_override={self.manual_cutting_depth is not None})")
        self.bar.display_value = f"{depth:.3f}" if is_metric else f"{depth:.4f}"
        return True  # advance to next step

    # Step 7
    def _start_threading_operation(self, *args):
        if not self.app.board.connected:
            self.stop()
            return False

        if not self._start_position_preloaded:
            log.warning("Threading requested without start preload")
            self.goto_step(5)
            return False

        if not self._check_valid_start_position():
            return False

        if not self._check_spindle_turning_forward():
            return False

        if not self._check_spindle_speed_for_pitch():
            return False

        log.info("Starting threaded cut to stop position: %s", self.bar.stop_position)
        self.bar.last_cutting_depth = self.cross_slide_input.encoderCurrent
        self.bar.action_button_enabled = False
        self.bar.retract_button_visible = False

        compound_z_offset = self._get_compound_z_offset_encoder()

        if compound_z_offset != 0:
            # Compound infeed mode: physically shift the saddle by ΔZ before latching
            target = self.bar.start_position + self._get_saddle_scale_effective_dir() * compound_z_offset
            log.info(f"Compound infeed: shifting saddle by {compound_z_offset} encoder counts to {target}")
            self._apply_reversing_adjusting_acceleration()
            self._command_move_to_encoder(target, speed=self.app.els.at_preload_adjust_speed)
            self._servo_watch_callback = self._watch_compound_z_move_done
            self.app.board.bind(update_tick=self._servo_watch_callback)
        else:
            self._prepare_and_send_thread_latch()

        return False

    def _watch_compound_z_move_done(self, *_):
        if not self._motion_complete():
            return
        self._reset_servo_watch_callback()
        log.info("Compound Z move complete, switching to threading acceleration and latching spindle")
        self._prepare_and_send_thread_latch()

    def _prepare_and_send_thread_latch(self):
        """Apply threading parameters, bind UI to servo, and send the latch command."""
        self._apply_threading_acceleration()
        self._apply_threading_max_speed()
        self.bar.bind_display_value_to_servo_position()
        self._send_thread_latch()

    def _send_thread_latch(self):
        """Write threading registers to firmware. threadRemainingSteps is calculated
        fresh from the current saddle position every pass."""
        if not self._check_saddle_not_past_stop():
            return

        threading_delta_steps = self._get_threading_servo_delta_steps()
        dev = self.app.board.device

        if not self._threading_started:
            self._threading_started = True
            self._threading_active_confirmed = False
            dev['assistedThreadingData']['threadRemainingSteps'] = threading_delta_steps
            dev['assistedThreadingData']['threadRequest'] = 1
        else:
            self._threading_active_confirmed = False
            dev['assistedThreadingData']['threadRemainingSteps'] = threading_delta_steps
            dev['assistedThreadingData']['threadEnabled'] = 1

        log.info(
            f"Threading latch sent: threadRemainingSteps={threading_delta_steps}, "
            f"servoCurrent={self.app.board.fast_data_values['servoCurrent']}, "
            f"saddle_current={self.saddle_input.encoderCurrent}, stop={self.bar.stop_position}"
        )

        self._servo_watch_callback = lambda *a: self._check_servo_threading_done(5, *a)
        self.app.board.bind(update_tick=self._servo_watch_callback)

    def _check_servo_threading_done(self, next_step: int, *args):
        dev = self.app.board.device
        dev['assistedThreadingData'].refresh()
        threadPhaseActive = dev['assistedThreadingData']['threadPhaseActive']
        threadEnabled = dev['assistedThreadingData']['threadEnabled']

        if log.isEnabledFor(logging.DEBUG):
            spindleScaleIndex = dev['assistedThreadingData']['spindleScaleIndex']
            log.debug(
                f"Checking servo done: "
                f"spindleScaleIndex={spindleScaleIndex}, "
                f"spindleCountsPerRev={dev['assistedThreadingData']['spindleCountsPerRev']}, "
                f"spindlePhaseTolerance={dev['assistedThreadingData']['spindlePhaseTolerance']}, "
                f"threadRequest={dev['assistedThreadingData']['threadRequest']}, "
                f"threadReset={dev['assistedThreadingData']['threadReset']}, "
                f"threadPhaseActive={threadPhaseActive}, "
                f"threadEnabled={threadEnabled}, "
                f"syncEnable={dev['scales'][spindleScaleIndex]['syncEnable']}, "
                f"threadPhaseRef={dev['assistedThreadingData']['threadPhaseRef']}, "
                f"currentThreadPhase={dev['assistedThreadingData']['currentThreadPhase']}, "
                f"spindleEncoderPosition={dev['scales'][spindleScaleIndex]['position']}, "
                f"threadRemainingSteps={dev['assistedThreadingData']['threadRemainingSteps']}, "
                f"threadStartSteps={dev['assistedThreadingData']['threadStartSteps']}, "
                f"desiredSteps={dev['servo']['desiredSteps']}, "
                f"currentSteps={dev['servo']['currentSteps']}, "
            )

        if threadEnabled == 1 or threadPhaseActive == 1:
            self._threading_active_confirmed = True

        if self._threading_active_confirmed and threadEnabled == 0 and threadPhaseActive == 0:
            log.info("Servo reached desired position")

            # Stop watching
            self._reset_servo_watch_callback()

            self.goto_step(next_step)

    # ---------------------------------------------------------------------------
    # Manual input keypads
    # ---------------------------------------------------------------------------

    def _open_stop_position_keypad(self, *args):
        from rcp.components.popups.keypad import Keypad

        is_metric = self.app.formats.current_format == "MM"

        keypad = Keypad(title="Enter Stop Length (" + ("mm" if is_metric else "in") + ")")
        keypad.integer = False

        def on_done(value):
            try:
                self.manual_stop_length = float(value)
                log.info(f"Manual stop length entered: {self.manual_stop_length}")
                # Display this override until user moves scale again
                self.bar.display_value = f"{self.manual_stop_length:.3f}" if is_metric else f"{self.manual_stop_length:.4f}"
            except ValueError:
                log.warning(f"Invalid stop length input: {value}")
            finally:
                self.bar.update_buttons_state()

        keypad.show_with_callback(callback_fn=on_done,
                                  current_value=self.manual_stop_length or 0.0)

    def _open_final_cutting_depth_position_keypad(self, *args):
        from rcp.components.popups.keypad import Keypad
        is_metric = self.app.formats.current_format == "MM"
        # Always use calculated depth as default
        calculated_depth = self._calculate_thread_depth()
        default_value = calculated_depth if calculated_depth is not None else 0.0
        depth_unit = "mm" if is_metric else "in"
        keypad = Keypad(title=f"Enter Final Cutting Depth ({depth_unit})")
        keypad.integer = False

        def on_done(value):
            try:
                self.manual_cutting_depth = abs(float(value))
                log.info(f"Manual cutting depth entered: {self.manual_cutting_depth}")
                self.bar.display_value = f"{self.manual_cutting_depth:.3f}" if is_metric else f"{self.manual_cutting_depth:.4f}"
                self.bar.action_button_enabled = True
            except ValueError:
                log.warning(f"Invalid cutting depth input: {value}")
                self.bar.action_button_enabled = False

        log.info(f"Opening cutting depth keypad with calculated default: {default_value:.4f}")
        keypad.show_with_callback(callback_fn=on_done,
                                  current_value=self.manual_cutting_depth if self.manual_cutting_depth is not None else default_value)

    # ---------------------------------------------------------------------------
    # Servo helpers
    # ---------------------------------------------------------------------------

    def _stop_servo(self):
        if not self.app.board.connected:
            return
        self.servo.set_max_speed(self.servo.maxSpeed)  # restore speed
        self.servo.servoEnable = 0  # disable
        self._apply_original_servo_acceleration()  # restore original acceleration if it was changed

    def _reset_servo_watch_callback(self):
        if self._servo_watch_callback:
            self.app.board.unbind(update_tick=self._servo_watch_callback)
            self._servo_watch_callback = None

    def _clear_bar_display(self):
        self.bar.unbind_all_display_value()
        self.bar.display_value = ""

    def _apply_original_servo_acceleration(self):
        self.app.board.device['servo']['acceleration'] = self.servo.acceleration

    def _apply_reversing_adjusting_acceleration(self):
        rate = self.app.els.at_reversing_adjusting_acceleration
        if rate and rate > 0:
            self.app.board.device['servo']['acceleration'] = rate
        else:
            self._apply_original_servo_acceleration()

    def _apply_threading_acceleration(self):
        rate = self.app.els.at_threading_acceleration
        if rate and rate > 0:
            self.app.board.device['servo']['acceleration'] = rate
        else:
            self._apply_original_servo_acceleration()

    def _apply_threading_max_speed(self):
        target_speed = self.app.els.at_threading_max_speed
        if target_speed and target_speed > 0:
            self.servo.set_max_speed(target_speed)
        else:
            self.servo.set_max_speed(self.servo.maxSpeed)

    # ---------------------------------------------------------------------------
    # Threading progress display
    # ---------------------------------------------------------------------------

    def _bind_threading_progress_display(self):
        """
        Bind display to show threading progress: "Last: <incremental_cut> | Rem: <remaining>"
        where:
        - Last = incremental cut since last_cutting_depth
        - Rem = remaining distance until final thread depth
        """
        self.bar.unbind_all_display_value()
        self._progress_display_scale = self.cross_slide_input

        def on_cross_slide_update(instance, value):
            try:
                is_metric = self.app.formats.current_format == "MM"
                current_encoder = self.cross_slide_input.encoderCurrent
                last_cutting_depth_encoder = self.bar.last_cutting_depth
                factor = float(self.app.formats.factor)

                scale_ratio = abs(Fraction(self.cross_slide_input.ratioNum, self.cross_slide_input.ratioDen) * factor)

                # Calculate incremental cut depth in encoder units
                incremental_cut_encoder = last_cutting_depth_encoder - current_encoder if self.bar.inner_thread else current_encoder - last_cutting_depth_encoder

                incremental_cut_display = incremental_cut_encoder * scale_ratio
                # Calculate remaining depth
                final_depth_encoder = current_encoder - self.bar.cutting_depth if self.bar.inner_thread else self.bar.cutting_depth - current_encoder
                remaining_display = final_depth_encoder * scale_ratio

                if self.bar.compound_infeed_mode:
                    # Show compound Z offset in saddle display units
                    z_enc = self._get_compound_z_offset_encoder()
                    saddle_inp = self.saddle_input
                    saddle_factor = float(self.app.formats.MM_FRACTION if is_metric else self.app.formats.INCHES_FRACTION)
                    saddle_scale_factor = abs(float(saddle_inp.ratioDen) / float(saddle_inp.ratioNum)) if saddle_inp.ratioNum != 0 else 1.0
                    z_display = z_enc * saddle_factor / saddle_scale_factor
                    if is_metric:
                        self.bar.display_value = f"Last: {incremental_cut_display:.3f} | Rem: {remaining_display:.3f} | Z+{z_display:.3f}"
                    else:
                        self.bar.display_value = f"Last: {incremental_cut_display:.4f} | Rem: {remaining_display:.4f} | Z+{z_display:.4f}"
                else:
                    if is_metric:
                        self.bar.display_value = f"Last: {incremental_cut_display:.3f} | Rem: {remaining_display:.3f}"
                    else:
                        self.bar.display_value = f"Last: {incremental_cut_display:.4f} | Rem: {remaining_display:.4f}"
                log.debug(f"Threading progress: incremental_cut={incremental_cut_display:.4f}, remaining={remaining_display:.4f}")
            except Exception as e:
                log.error(f"Error updating threading progress display: {e}")

        self._on_threading_progress_update = on_cross_slide_update
        self.cross_slide_input.bind(encoderCurrent=on_cross_slide_update)
        on_cross_slide_update(self.cross_slide_input, self.cross_slide_input.encoderCurrent)
