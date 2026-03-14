import cProfile
import io
import pstats
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

FRAME_HISTORY_SIZE = 300  # ~10 seconds at 30fps
PROFILE_DIR = Path.home() / ".config" / "rotary-controller-python" / "profiles"


class ProfilingPanel(BoxLayout):
    is_profiling = BooleanProperty(False)
    profile_results = StringProperty("")
    fps_current = NumericProperty(0)
    fps_min = NumericProperty(0)
    fps_max = NumericProperty(0)
    fps_avg = NumericProperty(0)
    frame_time_ms = NumericProperty(0)
    frame_time_max_ms = NumericProperty(0)
    status_text = StringProperty("Profiler idle")
    top_n = NumericProperty(30)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._profiler: cProfile.Profile | None = None
        self._fps_history: deque[float] = deque(maxlen=FRAME_HISTORY_SIZE)
        self._frame_times: deque[float] = deque(maxlen=FRAME_HISTORY_SIZE)
        self._last_frame_time: float = 0.0
        self._update_event = Clock.schedule_interval(self._update_stats, 1.0 / 5)
        self._frame_event = Clock.schedule_interval(self._track_frame, 0)

    def _track_frame(self, dt):
        """Called every frame to track frame timing."""
        now = time.perf_counter()
        if self._last_frame_time > 0:
            elapsed_ms = (now - self._last_frame_time) * 1000
            self._frame_times.append(elapsed_ms)
        self._last_frame_time = now

    def _update_stats(self, dt):
        """Update displayed FPS stats periodically."""
        self.fps_current = Clock.get_fps()
        if self._frame_times:
            self.frame_time_ms = self._frame_times[-1]
            self.frame_time_max_ms = max(self._frame_times)

        self._fps_history.append(self.fps_current)
        if self._fps_history:
            self.fps_min = min(self._fps_history)
            self.fps_max = max(self._fps_history)
            self.fps_avg = sum(self._fps_history) / len(self._fps_history)

    def toggle_profiling(self):
        if self.is_profiling:
            self.stop_profiling()
        else:
            self.start_profiling()

    def start_profiling(self):
        if self.is_profiling:
            return
        self._profiler = cProfile.Profile()
        self._profiler.enable()
        self.is_profiling = True
        self.status_text = "Profiling active... reproduce the slowdown, then stop."
        self.profile_results = ""
        log.info("cProfile started")

    def stop_profiling(self):
        if not self.is_profiling or self._profiler is None:
            return
        self._profiler.disable()
        self.is_profiling = False
        self.status_text = "Profiler stopped. Results below."
        log.info("cProfile stopped")
        self._format_results()

    def _format_results(self):
        if self._profiler is None:
            return

        stream = io.StringIO()
        stats = pstats.Stats(self._profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(self.top_n)

        result = stream.getvalue()

        # Also get a time-sorted view
        stream2 = io.StringIO()
        stats2 = pstats.Stats(self._profiler, stream=stream2)
        stats2.strip_dirs()
        stats2.sort_stats(pstats.SortKey.TIME)
        stats2.print_stats(self.top_n)

        text_report = (
            "=== Sorted by CUMULATIVE time ===\n"
            + result
            + "\n=== Sorted by INTERNAL time ===\n"
            + stream2.getvalue()
        )

        saved_path = self._save_profile(text_report)
        self.profile_results = text_report
        if saved_path:
            self.status_text = f"Saved to {saved_path}"

    def _save_profile(self, text_report: str) -> Path | None:
        try:
            PROFILE_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save binary .prof (for snakeviz / PyCharm / cProfile viewers)
            prof_path = PROFILE_DIR / f"profile_{timestamp}.prof"
            self._profiler.dump_stats(str(prof_path))

            # Save human-readable text report
            txt_path = PROFILE_DIR / f"profile_{timestamp}.txt"
            txt_path.write_text(text_report)

            log.info(f"Profile saved: {prof_path} and {txt_path}")
            return PROFILE_DIR
        except OSError as e:
            log.error(f"Failed to save profile: {e}")
            return None

    def reset_stats(self):
        """Reset all collected stats."""
        self._fps_history.clear()
        self._frame_times.clear()
        self.fps_min = 0
        self.fps_max = 0
        self.fps_avg = 0
        self.frame_time_ms = 0
        self.frame_time_max_ms = 0
        self.profile_results = ""
        self.status_text = "Stats reset"
        self._profiler = None