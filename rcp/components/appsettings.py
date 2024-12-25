import os.path
from kivy.logger import Logger
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar

log = Logger.getChild("app-settings")

INPUTS_COUNT = 4

config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
)
config = ConfigParser()
config.read(config_path)
