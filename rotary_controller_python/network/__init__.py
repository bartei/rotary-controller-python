import datetime
import shutil
import subprocess
import logging
import os

from rotary_controller_python.network import models

log = logging.getLogger(__name__)


def read_interfaces(config_path: str = "/etc/network/interfaces"):
    interface = models.NetworkInterface(
        name="wlan0",
        dhcp=False,
        wireless=models.Wireless(
            password="",
            ssid=""
        )
    )

    if not os.path.exists(config_path):
        return interface

    with open(config_path, "r") as f:
        lines = f.readlines()

    lines = [item for item in lines if not item.strip().startswith("#")]
    for line in lines:
        tokens = line.strip().split(" ")
        if len(tokens) < 2:
            continue

        if tokens[0] == "iface":
            interface.name = tokens[1]
            if tokens[3] == "dhcp":
                interface.dhcp = True
            else:
                interface.dhcp = False

        if tokens[0] == "address":
            interface.address, interface.netmask = tokens[1].split("/")

        if tokens[0] == "gateway":
            interface.gateway = tokens[1]

        if tokens[0] == "wpa-ssid":
            interface.wireless.ssid = tokens[1]

        if tokens[0] == "wpa-psk":
            interface.wireless.password = tokens[1]

    return interface


def render_interfaces(configuration: models.NetworkInterface, output_file: str = "/etc/network/interfaces"):
    if not os.path.exists(os.path.dirname(output_file)):
        log.error("Destination folder not found! {}")
        # return

    if os.path.exists(output_file):
        log.info("Saving a backup of the existing configuration values")
        shutil.move(src=output_file, dst=f"{output_file}.backup.{datetime.datetime.now().isoformat()}")

    with open(output_file, "w") as f:
        f.write(f"auto {configuration.name}\n")

        if configuration.dhcp:
            f.write(f"iface {configuration.name} inet dhcp\n")
        else:
            f.write(f"iface {configuration.name} inet static\n")
            f.write(f"    address {configuration.address}/{configuration.netmask}\n")
            f.write(f"    gateway {configuration.gateway}\n")

        if configuration.wireless is not None:
            if configuration.wireless.ssid is not None and len(configuration.wireless.ssid) > 0:
                f.write(f"    wpa-ssid {configuration.wireless.ssid}\n")
            if configuration.wireless.password is not None and len(configuration.wireless.password) > 0:
                f.write(f"    wpa-psk {configuration.wireless.password}\n")

    log.info(f"Generation complete")


def reload_interfaces():
    log.info("Call ifreload to reconfigure the network settings")

    result = subprocess.run(["which", "ifreload"], timeout=1, text=True)
    if result.returncode != 0:
        message = "ifreload is not available on this system, install ifupdown2 to allow dynamic configuration changes"
        log.error(message)
        return message

    reload = subprocess.run(["ifreload", "-av"])
    return reload.stdout
