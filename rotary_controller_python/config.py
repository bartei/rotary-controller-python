import os

from kivy.config import ConfigParser

config = ConfigParser()
config.read(os.path.dirname(__file__) + "/../config.ini")
