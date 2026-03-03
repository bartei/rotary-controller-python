import os

import sentry_sdk
from kivy.app import App
from kivy.properties import ObjectProperty, ConfigParserProperty, NumericProperty, ListProperty, StringProperty
from kivy.logger import Logger
log = Logger.getChild(__name__)

from rcp.components.appsettings import config
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.board import Board
from rcp.dispatchers.els import ElsDispatcher
from rcp.dispatchers.formats import FormatsDispatcher
from rcp.dispatchers.scale import ScaleDispatcher
from rcp.dispatchers.servo import ServoDispatcher


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

    servo: ServoDispatcher = ObjectProperty()

    scales: list[ScaleDispatcher] = ListProperty()

    axes: list[AxisDispatcher] = ListProperty()

    els: ElsDispatcher = ObjectProperty()

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
        return self.board.get_spindle_scale()

    def get_spindle_axis(self):
        return self.board.get_spindle_axis()

    def build(self):
        self.formats = FormatsDispatcher(id_override="0")
        self.board = Board(formats=self.formats, offset_provider=self)

        if not self.formats.disable_error_reporting:
            log.info("Error reporting is enabled, configuring Sentry")
            sentry_sdk.init(
                dsn="https://8fd20c0607e9c930a16d51a4b1eacc94@o4509625403506688.ingest.us.sentry.io/4509625405014016",
                send_default_pii=False,
                traces_sample_rate=0.2,
            )

        # Backward compat aliases — most KV files use app.servo / app.scales / app.axes
        self.servo = self.board.servo
        self.scales = list(self.board.scales)
        self.axes = list(self.board.axes)

        self.els = ElsDispatcher(id_override="0")

        self.beep()

        import importlib.metadata
        self.version = "v" + importlib.metadata.version("rcp")

        from rcp.components.manager import Manager
        self.manager = Manager()
        return self.manager
