import logging
import os
import time
import collections

from decimal import Decimal

from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.config import config

log = logging.getLogger(__file__)
app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout):
    # Configuration Values
    scale_input = NumericProperty(defaultvalue=0)
    scale_positions = ListProperty()
    section = StringProperty(defaultvalue="axis")
    axis_name = StringProperty(defaultvalue="NN")
    ratio_num = NumericProperty(defaultvalue=1)
    ratio_den = NumericProperty(defaultvalue=200)
    sync_num = NumericProperty(defaultvalue=1)
    sync_den = NumericProperty(defaultvalue=100)
    sync_enable = StringProperty(defaultvalue="normal")

    # Those get loaded and managed at runtime
    formatted_axis_speed = NumericProperty(0.000)

    def __init__(self, **kv):
        super(CoordBar, self).__init__(**kv)
        self.config_parser = config
        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        Clock.schedule_interval(self.update_speed, 1.0 / 10)

    def on_section(self, instance, value):
        instance.reload_properties()
        self.bind(
            ratio_num=self.save_properties,
            ratio_den=self.save_properties,
            sync_num=self.save_properties,
            sync_den=self.save_properties,
        )

    def reload_properties(self):
        if self.config_parser is not None:
            self.axis_name = self.config_parser.getdefault(self.section, option="axis_name", defaultvalue="NN")
            self.ratio_num = int(Decimal(
                self.config_parser.getdefault(self.section, option="ratio_num", defaultvalue=1)
            ))
            self.ratio_den = int(Decimal(
                self.config_parser.getdefault(self.section, option="ratio_den", defaultvalue=200)
            ))
            self.sync_num = int(Decimal(
                self.config_parser.getdefault(self.section, option="sync_num", defaultvalue=1)
            ))
            self.sync_den = int(Decimal(
                self.config_parser.getdefault(self.section, option="sync_den", defaultvalue=100)
            ))
            self.sync_enable = self.config_parser.getdefault(self.section, option="sync_enable", defaultvalue="normal")
        else:
            log.info("the config parser is not available!")

    def save_properties(self, instance=None, value=None):
        if self.config_parser is not None:
            self.config_parser: ConfigParser
            self.config_parser.set(section=self.section, option="sync_num", value=self.sync_num.__str__())
            self.config_parser.set(section=self.section, option="sync_den", value=self.sync_den.__str__())
            self.config_parser.set(section=self.section, option="sync_enable", value=self.sync_enable)
            self.config_parser.write()

    def update_speed(self, *args, **kv):
        current_time = time.time()

        # Calculate axis speed
        self.speed_history.append(
            (Decimal(self.scale_positions[self.scale_input]) - self.previous_axis_pos) /
            Decimal(current_time - self.previous_axis_time)
        )

        average = (sum(self.speed_history) / Decimal(len(self.speed_history)))

        if app.current_units == "in":
            # Speed in feet per minute
            self.formatted_axis_speed = float(average * 60 / Decimal("25.4") / 12)
        else:
            # Speed in mt/minute
            self.formatted_axis_speed = float(average * 60 / 1000)

        self.previous_axis_time = current_time
        self.previous_axis_pos = Decimal(self.scale_positions[self.scale_input])

    def on_sync_enable(self, instance, value):
        self.save_properties()
        # self.device.set_sync(
        #     encoder_index=self.scale_input,
        #     sync_status=True if value == "down" else False
        # )

    @property
    def set_position(self):
        return 0

    @set_position.setter
    def set_position(self, value):
        try:
            decimal_value = Decimal(self.ratio_den) / Decimal(self.ratio_num) * Decimal(value)
            int_value = int(decimal_value)
            self.device.set_encoder_value(
                encoder_index=self.scale_input,
                encoder_value=int_value
            )
        except Exception as e:
            log.exception(e.__str__())
