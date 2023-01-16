import logging
import os
import time
import collections

from decimal import Decimal

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ConfigParserProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from components.appsettings import config


log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout):
    release_function = None
    input_name = StringProperty()
    axis_pos = NumericProperty(0.0)
    formatted_axis_pos = StringProperty("0.000")
    formatted_axis_speed = StringProperty("0.000")

    metric_pos_format = StringProperty()
    metric_speed_format = StringProperty()

    imperial_pos_format = StringProperty()
    imperial_speed_format = StringProperty()

    current_units = StringProperty("mm")

    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config
    )

    def __init__(self, *args, **kv):
        super(CoordBar, self).__init__(**kv)

        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)

        self.bind(metric_pos_format=self.on_axis_pos)
        self.bind(imperial_pos_format=self.on_axis_pos)
        self.bind(current_units=self.on_axis_pos)
        self.bind(current_units=self.update_labels)
        Clock.schedule_interval(self.update_speed, 1.0 / 10)

    def on_input_name(self, instance, value):
        if self.input_name != '':
            bind_definition = dict()
            bind_definition[self.input_name] = self.setter('axis_pos')
            app = App.get_running_app()
            app.bind(**bind_definition)

    def update_labels(self, *args, **kv):
        if self.current_units == "in":
            self.speed_label = "Speed (feet/min)"
            self.position_label = "Pos (in)"
        else:
            self.speed_label = "Speed (m/min)"
            self.position_label = "Pos (mm)"

    def on_axis_pos(self, *args, **kv):
        try:
            decimal_value = Decimal(self.axis_pos)

            if self.current_units == "in":
                self.formatted_axis_pos = (
                    self.imperial_pos_format.format(decimal_value / Decimal("25.4")).replace("+", " ")
                )
            else:
                self.formatted_axis_pos = self.metric_pos_format.format(decimal_value).replace("+", " ")

        except Exception as e:
            log.exception(e.__str__())
            self.formatted_axis_pos = "0"

    def update_speed(self, *args, **kv):
        current_time = time.time()

        # Calculate axis speed
        self.speed_history.append(
            (Decimal(self.axis_pos) - self.previous_axis_pos) /
            Decimal(current_time - self.previous_axis_time)
        )

        average = (
            sum(self.speed_history) /
            Decimal(len(self.speed_history))
        )

        if self.current_units == "in":
            # Speed in feet per minute
            self.formatted_axis_speed = self.imperial_speed_format.format(
                average * 60 / Decimal("25.4") / 12
            )
        else:
            # Speed in mt/minute
            self.formatted_axis_speed = self.metric_speed_format.format(
                average * 60 / 1000
            )

        self.previous_axis_time = current_time
        self.previous_axis_pos = Decimal(self.axis_pos)
