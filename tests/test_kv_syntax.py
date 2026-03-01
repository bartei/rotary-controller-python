import glob
import os

import pytest
from kivy.lang.parser import Parser, ParserException


def get_kv_files():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return glob.glob(os.path.join(project_root, "rcp", "**", "*.kv"), recursive=True)


@pytest.mark.parametrize("kv_file", get_kv_files(), ids=lambda p: os.path.relpath(p))
def test_kv_file_syntax(kv_file):
    """Verify all .kv files have valid KV syntax (catches indentation errors, etc.)."""
    with open(kv_file) as f:
        content = f.read()
    # Strip import directives to avoid triggering module imports during parsing
    lines = content.split("\n")
    filtered = "\n".join(l for l in lines if not l.strip().startswith("#:"))
    try:
        Parser(content=filtered, filename=kv_file)
    except ParserException as e:
        pytest.fail(f"KV parse error in {kv_file}: {e}")
