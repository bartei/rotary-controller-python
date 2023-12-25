import pprint

from jinja2 import Environment, FileSystemLoader, select_autoescape

from rotary_controller_python.network.models import Wireless, NetworkInterface
from rotary_controller_python.network import reload_interfaces

def test_ifreload():
    result = reload_interfaces()
