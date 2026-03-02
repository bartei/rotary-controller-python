from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

load_kv(__file__)


class ServoBar(BoxLayout):
    """Pure UI widget displaying servo state. All logic lives in ServoDispatcher."""
    pass
