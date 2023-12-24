from imaplib import Literal
from typing import Optional
import pprint

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel


class Wireless(BaseModel):
    password: Optional[str]
    ssid: str


class NetworkInterface(BaseModel):
    name: str
    dhcp: bool
    address: Optional[str]
    gateway: Optional[str]
    wireless: Optional[Wireless]


def test_wlan0_dhcp():
    data = NetworkInterface(
        name="wlan0",
        dhcp=True,
        wireless=Wireless(
            password="test_password",
            ssid="test_ssid",
        )
    )

    pprint.pp(data.dict())

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True
    )

    template = env.get_template("interfaces.jinja2")
    output = template.render(interface=data.dict())
    print(output)


def test_eth0_static():
    data = NetworkInterface(
        name="eth0",
        dhcp=False,
        address="10.1.2.250/24",
        gateway="10.1.2.1",
    )

    pprint.pp(data.dict())

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True
    )

    template = env.get_template("interfaces.jinja2")
    output = template.render(interface=data.dict())
    print(output)
    expected_result = """
iface eth0 inet static
    address 10.1.2.250/24
    gateway 10.1.2.1
"""

    assert expected_result in output


def test_wlan0_static():
    data = NetworkInterface(
        name="wlan0",
        dhcp=False,
        address="10.1.2.250/24",
        gateway="10.1.2.1",
        wireless=Wireless(
            password="test_password",
            ssid="test_ssid",
        )
    )

    pprint.pp(data.dict())

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True
    )

    template = env.get_template("interfaces.jinja2")
    output = template.render(interface=data.dict())
    print(output)

    expected_result = """
iface wlan0 inet static
    address 10.1.2.250/24
    gateway 10.1.2.1
    wpa-psk test_password
    wpa-ssid test_ssid
"""
    assert expected_result in output
