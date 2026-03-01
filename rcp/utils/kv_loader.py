import os

from kivy.lang import Builder
from kivy.logger import Logger

log = Logger.getChild(__name__)

_loaded_kv_files: set[str] = set()


def load_kv(source_file: str) -> str | None:
    """
    Load the .kv file corresponding to a Python source file.

    Resolves the .kv path by replacing the .py extension, checks for duplicates,
    and loads via Kivy's Builder if the file exists.

    Args:
        source_file: The __file__ of the calling module.

    Returns:
        The resolved .kv file path if loaded, None otherwise.
    """
    kv_file = os.path.join(os.path.dirname(source_file), source_file.replace(".py", ".kv"))
    kv_file = os.path.abspath(kv_file)

    if kv_file in _loaded_kv_files:
        log.warning(f"KV file already loaded, skipping duplicate: {kv_file}")
        return None

    if not os.path.exists(kv_file):
        return None

    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)
    _loaded_kv_files.add(kv_file)
    return kv_file


def get_loaded_kv_files() -> set[str]:
    """Return the set of all KV files that have been loaded."""
    return _loaded_kv_files.copy()