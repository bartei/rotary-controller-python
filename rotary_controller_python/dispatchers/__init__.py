from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from loguru import logger as log
from rotary_controller_python.configurator import read_settings, write_settings


class SavingDispatcher(EventDispatcher):
    _skip_save = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Read the settings from file and into a dictionary
        self.read_settings()
        self.bind_settings()

    def get_our_properties(self):
        our_elements = dir(type(self))
        properties = [getattr(type(self), item) for item in our_elements]
        properties = [
            item
            for item in properties
            if type(item) in [NumericProperty, StringProperty, BooleanProperty]
        ]
        properties = [item for item in properties if item.name not in self._skip_save]
        return properties

    @staticmethod
    def get_writeable_properties(klass):
        return [
            attr
            for attr, value in vars(klass).items()
            if isinstance(value, property) and value.fset is not None
        ]

    @property
    def filename(self):
        return f"{self.__class__.__name__}-{self.uid}.yaml"

    def read_settings(self):
        props = self.get_our_properties()
        prop_names = [item.name for item in props]

        config_data = read_settings(self.filename)
        if config_data is None:
            self.save_settings()
            return

        for k, v in config_data.items():
            if k in prop_names:
                self.__setattr__(k, v)
            else:
                log.info(f"Provided property with name: {k} is unknown to this class")

    def bind_settings(self):
        props = self.get_our_properties()
        prop_names = [item.name for item in props]

        kwargs = {item: self.save_settings for item in prop_names}
        self.bind(**kwargs)

    def save_settings(self, *args, **kv):
        props = self.get_our_properties()
        prop_names = [item.name for item in props]
        data = dict()
        for item in prop_names:
            data[item] = self.__getattribute__(item)

        write_settings(self.filename, data)
