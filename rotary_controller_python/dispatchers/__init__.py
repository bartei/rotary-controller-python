import os
import shutil
from pathlib import Path

import yaml
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty, ObservableList

log = Logger.getChild(__name__)


class SavingDispatcher(EventDispatcher):
    _skip_save = []
    _force_save = []
    id_override = StringProperty("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check if we have an id_override
        if self.id_override == "":
            self.id_override = f"{self.uid}"

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

        force_properties = [getattr(type(self), item) for item in self._force_save]
        properties.extend(force_properties)
        return properties

    @property
    def filename(self):
        home_folder = os.environ.get('HOME')
        settings_folder = Path(home_folder) / ".config" / "rotary-controller-python"
        os.makedirs(settings_folder, exist_ok=True)

        settings_path = settings_folder / f"{self.__class__.__name__}-{self.id_override}.yaml"
        log.debug(f"Identified settings path as: {settings_path}")
        return settings_path

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
            if isinstance(data[item], ObservableList):
                data[item] = list(data[item])

        write_settings(self.filename, data)


def read_settings(file: str):
    if not os.path.exists(file):
        return None

    try:
        with open(file, "r") as f:
            data = yaml.safe_load(f.read())
            return data
    except Exception as e:
        log.error(e.__str__())
        return None


def write_settings(file: str, data):
    try:
        with open(file, "w") as f:
            yaml.dump(data, f)
        return True

    except Exception as e:
        log.error(e.__str__())
        return False
