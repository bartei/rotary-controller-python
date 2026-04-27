from fractions import Fraction

from kivy.logger import Logger

log = Logger.getChild(__name__)


class GoToStartPhase:
    IDLE = 0
    RETRACT = 1
    PRELOAD = 2
    ADJUST = 3


class AssistedThreadingMotionMixin:
    # ---------------------------------------------------------------------------
    # Step 6 callback — go to start (motion logic only)
    # ---------------------------------------------------------------------------

    def _go_to_start(self, *args):
        if not self.app.board.connected:
            self.stop()
            return False

        self.bar.retract_button_enabled = False  # Disable retract button during move to start
        self.bar.action_button_enabled = False  # Disable action button during move to start

        self._apply_reversing_adjusting_acceleration()
        self._start_position_preloaded = False
        self._goto_start_phase = GoToStartPhase.RETRACT

        effective_dir = self._get_saddle_scale_effective_dir()

        retraction = abs(self._get_saddle_backlash_distance_encoder_steps() * 1.5)  # retract 1.5x backlash distance
        retraction_dir = -effective_dir  # retract opposite to cutting direction
        log.info(f"Starting retract to go to start: effective_dir={effective_dir}, retraction={retraction}, retraction_dir={retraction_dir}")
        retract_target = self.bar.start_position + retraction_dir * retraction

        self._command_move_to_encoder(retract_target, speed=self.app.els.at_reversing_speed)

        self._servo_watch_callback = self._watch_go_to_start
        self.app.board.bind(update_tick=self._servo_watch_callback)

        return False

    # ---------------------------------------------------------------------------
    # Low-level move command
    # ---------------------------------------------------------------------------

    def _command_move_to_encoder(self, target_encoder, speed):
        self._reset_encoder_stability_check()

        current_enc = self.saddle_input.encoderCurrent

        scale_ratio = Fraction(abs(self.saddle_input.ratioNum), abs(self.saddle_input.ratioDen))
        servo_ratio = Fraction(abs(self.servo.ratioNum), abs(self.servo.ratioDen))

        delta = int((target_encoder - current_enc) * scale_ratio / servo_ratio)

        log.info(
            f"Move to encoder: current={current_enc}, "
            f"target={target_encoder}, delta={delta}"
        )

        self.bar.bind_display_value_to_servo_position()
        self.servo.set_max_speed(speed)
        self.app.board.device['servo']['direction'] = delta

    # ---------------------------------------------------------------------------
    # Watch callbacks (polled on update_tick)
    # ---------------------------------------------------------------------------

    def _watch_retracting_stopped(self, *_):
        if not self._encoder_is_stable(self.app.els.at_saddle_encoder_stability_tolerance, self.app.els.at_saddle_encoder_stability_samples):
            return

        self._reset_servo_watch_callback()
        self.servo.set_max_speed(self.servo.maxSpeed)
        self.servo.servoEnable = 1  # back to normal servo mode

        self.goto_step(5)  # Go back to step 6 - Go to start position

    def _watch_go_to_start(self, *_):
        if not self._motion_complete():
            return

        if self._goto_start_phase == GoToStartPhase.RETRACT:
            self._start_preload_move()

        elif self._goto_start_phase == GoToStartPhase.PRELOAD:
            self._start_adjust_move()

        elif self._goto_start_phase == GoToStartPhase.ADJUST:
            self._finish_go_to_start()

    # ---------------------------------------------------------------------------
    # Encoder stability check
    # ---------------------------------------------------------------------------

    def _reset_encoder_stability_check(self):
        self._last_saddle_encoder_value = None
        self._stable_count = 0

    def _encoder_is_stable(self, tolerance, samples):
        current = self.saddle_input.encoderCurrent

        if self._last_saddle_encoder_value is None:
            self._last_saddle_encoder_value = current
            self._stable_count = 0
            return False

        if abs(current - self._last_saddle_encoder_value) <= tolerance:
            self._stable_count += 1
        else:
            self._stable_count = 0

        self._last_saddle_encoder_value = current

        return self._stable_count >= samples

    def _motion_complete(self):
        if self.app.board.fast_data_values['stepsToGo'] != 0:
            return False

        if not self._encoder_is_stable(self.app.els.at_saddle_encoder_stability_tolerance, self.app.els.at_saddle_encoder_stability_samples):
            return False

        return True

    # ---------------------------------------------------------------------------
    # Preload / adjust / finish phases
    # ---------------------------------------------------------------------------

    def _start_preload_move(self):
        self._reset_servo_watch_callback()
        self._goto_start_phase = GoToStartPhase.PRELOAD

        log.info("Retract complete, starting preload move")
        backlash_preload_steps = int(abs(self._get_saddle_backlash_distance_encoder_steps()) * 1.25)  # preload 1.25x backlash distance - before we retracted 1.5x so we have some cushion
        preload_target = self.saddle_input.encoderCurrent + self._get_saddle_scale_effective_dir() * backlash_preload_steps

        self._apply_reversing_adjusting_acceleration()
        self._command_move_to_encoder(
            preload_target,
            speed=self.app.els.at_preload_adjust_speed
        )

        self._servo_watch_callback = self._watch_go_to_start
        self.app.board.bind(update_tick=self._servo_watch_callback)

    def _start_adjust_move(self):
        self._reset_servo_watch_callback()
        self._goto_start_phase = GoToStartPhase.ADJUST

        log.info("Preload move complete, starting final adjust move")

        self._apply_reversing_adjusting_acceleration()
        self._command_move_to_encoder(
            self.bar.start_position,
            speed=self.app.els.at_preload_adjust_speed
        )

        self._servo_watch_callback = self._watch_go_to_start
        self.app.board.bind(update_tick=self._servo_watch_callback)

    def _finish_go_to_start(self):
        self._reset_servo_watch_callback()

        log.info("Start position reached with backlash preloaded")

        self._start_position_preloaded = True

        next_step = self.current_step + 1
        if self._is_cross_slide_at_final_cutting_depth():
            next_step += 1

        self.goto_step(next_step)
