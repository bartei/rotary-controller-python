
from rotary_controller_python.utils.base_device import BaseDevice
from rotary_controller_python.utils.communication import DeviceManager


class Global(BaseDevice):
    def __init__(self, device: DeviceManager, base_address: int):
        super().__init__(device=device)
        from rotary_controller_python.utils.addresses import GlobalAddresses
        self.addresses = GlobalAddresses(base_address)

    @property
    def execution_interval(self):
        return self.read_long(self.addresses.execution_interval)

    @property
    def execution_cycles(self):
        return self.read_long(self.addresses.execution_cycles)


class Index(BaseDevice):
    def __init__(self, device: DeviceManager, base_address: int):
        super().__init__(device=device)
        from rotary_controller_python.utils.addresses import IndexAddresses
        self.addresses = IndexAddresses(base_address)

    @property
    def divisions(self):
        return self.read_long(self.addresses.divisions)

    @divisions.setter
    def divisions(self, value):
        self.write_long(self.addresses.divisions, value)

    @property
    def index(self):
        return self.read_long(self.addresses.index)

    @index.setter
    def index(self, value):
        self.write_long(self.addresses.index, value)


class Servo(BaseDevice):
    def __init__(self, device: DeviceManager, base_address: int):
        super().__init__(device=device)
        from rotary_controller_python.utils.addresses import ServoAddresses
        self.addresses = ServoAddresses(base_address)

    @property
    def min_speed(self):
        return self.read_float(self.addresses.min_speed)

    @min_speed.setter
    def min_speed(self, value):
        self.write_float(self.addresses.min_speed, value)

    @property
    def max_speed(self):
        return self.read_float(self.addresses.max_speed)

    @max_speed.setter
    def max_speed(self, value):
        self.write_float(self.addresses.max_speed, value)

    @property
    def current_speed(self):
        return self.read_float(self.addresses.current_speed)

    @property
    def acceleration(self):
        return self.read_float(self.addresses.acceleration)

    @acceleration.setter
    def acceleration(self, value):
        self.write_float(self.addresses.acceleration, value)

    @property
    def absolute_offset(self):
        return self.read_float(self.addresses.absolute_offset)

    @absolute_offset.setter
    def absolute_offset(self, value):
        self.write_float(self.addresses.absolute_offset, value)

    @property
    def index_offset(self):
        return self.read_float(self.addresses.index_offset)

    @property
    def sync_offset(self):
        return self.read_float(self.addresses.sync_offset)

    @property
    def desired_position(self):
        return self.read_float(self.addresses.desired_position)

    @property
    def current_position(self):
        return self.read_float(self.addresses.current_position)

    @property
    def current_steps(self):
        return self.read_float(self.addresses.current_steps)

    @property
    def desired_steps(self):
        return self.read_float(self.addresses.desired_steps)

    @property
    def ratio_num(self):
        return self.read_long(self.addresses.ratio_num)

    @ratio_num.setter
    def ratio_num(self, value):
        self.write_long(self.addresses.ratio_num, value)

    @property
    def ratio_den(self):
        return self.read_long(self.addresses.ratio_den)

    @ratio_den.setter
    def ratio_den(self, value):
        self.write_long(self.addresses.ratio_den, value)

    @property
    def max_value(self):
        return self.read_long(self.addresses.max_value)

    @max_value.setter
    def max_value(self, value):
        self.write_long(self.addresses.max_value, value)

    @property
    def min_value(self):
        return self.read_long(self.addresses.min_value)

    @min_value.setter
    def min_value(self, value):
        self.write_long(self.addresses.min_value, value)

    @property
    def breaking_space(self):
        return self.read_float(self.addresses.breaking_space)

    @property
    def breaking_time(self):
        return self.read_float(self.addresses.breaking_time)

    @property
    def allowed_error(self):
        return self.read_float(self.addresses.allowed_error)


class Scale(BaseDevice):
    def __init__(self, device: DeviceManager, base_address: int):
        super().__init__(device=device)
        from rotary_controller_python.utils.addresses import ScaleAddresses
        self.addresses = ScaleAddresses(base_address)

    @property
    def encoder_previous(self):
        return self.read_unsigned(self.addresses.encoder_previous)

    @property
    def encoder_current(self):
        return self.read_unsigned(self.addresses.encoder_current)

    @property
    def ratio_num(self):
        return self.read_long(self.addresses.ratio_num)

    @ratio_num.setter
    def ratio_num(self, value):
        self.write_long(self.addresses.ratio_num, value)

    @property
    def ratio_den(self):
        return self.read_long(self.addresses.ratio_den)

    @ratio_den.setter
    def ratio_den(self, value):
        self.write_long(self.addresses.ratio_den, value)

    @property
    def max_value(self):
        return self.read_long(self.addresses.max_value)

    @max_value.setter
    def max_value(self, value):
        self.write_long(self.addresses.max_value, value)

    @property
    def min_value(self):
        return self.read_long(self.addresses.min_value)

    @min_value.setter
    def min_value(self, value):
        self.write_long(self.addresses.min_value, value)

    @property
    def position(self):
        return self.read_long(self.addresses.position)

    @position.setter
    def position(self, value):
        self.write_long(self.addresses.position, value)

    @property
    def error(self):
        return self.read_long(self.addresses.error)

    @property
    def sync_ratio_num(self):
        return self.read_long(self.addresses.sync_ratio_num)

    @sync_ratio_num.setter
    def sync_ratio_num(self, value):
        self.write_long(self.addresses.sync_ratio_num, value)

    @property
    def sync_ratio_den(self):
        return self.read_long(self.addresses.sync_ratio_den)

    @sync_ratio_den.setter
    def sync_ratio_den(self, value):
        self.write_long(self.addresses.sync_ratio_den, value)

    @property
    def sync_motion(self):
        return bool(self.device.read_register(self.addresses.sync_motion))

    @sync_motion.setter
    def sync_motion(self, value: bool):
        self.device.write_register(self.addresses.sync_motion, int(value))
