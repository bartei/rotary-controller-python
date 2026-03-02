import os
from typing import List

import sentry_sdk
from kivy.app import App
from kivy.properties import ObjectProperty, ConfigParserProperty, NumericProperty, ListProperty, StringProperty
from kivy.logger import Logger
log = Logger.getChild(__name__)

from rcp.components.appsettings import config
from rcp.components.home.coordbar import CoordBar
from rcp.components.home.servobar import ServoBar
from rcp.dispatchers.board import Board
from rcp.dispatchers.formats import FormatsDispatcher


class MainApp(App):
    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config,
    )

    formats = ObjectProperty()
    abs_inc = ConfigParserProperty(
        defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str
    )
    currentOffset = NumericProperty(0)

    tool = NumericProperty(0)

    board = ObjectProperty()

    home = ObjectProperty()

    servo: ServoBar = ObjectProperty()

    scales: List[CoordBar] = ListProperty()

    current_mode = ConfigParserProperty(
        defaultvalue=1, section="device", key="current_mode", config=config, val_type=int
    )

    scales_count = ConfigParserProperty(
        defaultvalue=4, section="device", key="scales_count", config=config, val_type=int
    )

    manager = ObjectProperty()

    version = StringProperty()

    def __init__(self, **kv):
        super().__init__(**kv)


    def beep(self, *args, **kv):
        pass
        # self.sound.volume = self.formats.volume
        # self.sound.play()

    @staticmethod
    def load_help(help_file_name):
        """
        Loads the specified help file text from the help files folder.
        """
        help_file_path = os.path.join(
            os.path.dirname(__file__),
            "help",
            help_file_name
        )
        if not os.path.exists(help_file_path):
            return "Help file not found"

        with open(help_file_path, "r") as f:
            return f.read()

    def set_mode(self, mode_id: int):
        self.current_mode = mode_id

    def get_spindle_scale(self):
        """
        Returns the current spindle scale if there is one configured, otherwise None
        """
        filtered_scales = [item for item in self.scales if item.spindleMode is True]
        if len(filtered_scales) != 1:
            return None
        return filtered_scales[0]

    def build(self):
        self.formats = FormatsDispatcher(id_override="0")
        self.board = Board()

        if not self.formats.disable_error_reporting:
            log.info("Error reporting is enabled, configuring Sentry")
            sentry_sdk.init(
                dsn="https://8fd20c0607e9c930a16d51a4b1eacc94@o4509625403506688.ingest.us.sentry.io/4509625405014016",
                send_default_pii=False,
                traces_sample_rate=0.2,
            )

        self.servo = ServoBar(id_override="0")
        for i in range(4):
            self.scales.append(CoordBar(inputIndex=i, device=self.board.device, id_override=f"{i}"))

        self.beep()

        import importlib.metadata
        self.version = "v" + importlib.metadata.version("rcp")

        from rcp.components.manager import Manager
        self.manager = Manager()
        return self.manager
