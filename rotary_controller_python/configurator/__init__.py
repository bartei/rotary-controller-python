import shutil

from loguru import logger as log
import os.path

import yaml


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
    if os.path.exists(file):
        shutil.move(file, f"{file}.old")

    try:
        with open(file, "w") as f:
            yaml.dump(data, f)
        return True

    except Exception as e:
        log.error(e.__str__())
        return False
