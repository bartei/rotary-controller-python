from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class HelpPopup(ModalView):
    help_text = StringProperty("")

    @staticmethod
    def show_help(help_file: str):
        if not help_file:
            return
        from rcp.app import MainApp
        app = MainApp.get_running_app()
        text = app.load_help(help_file)
        popup = HelpPopup(help_text=text)
        popup.open()