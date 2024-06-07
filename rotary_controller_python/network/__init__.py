import datetime
import json
import shutil
import subprocess
import logging
import os

from rotary_controller_python.network import models
from rotary_controller_python.network.models import RfkillStatus

log = logging.getLogger(__name__)


def read_interfaces(config_path: str = "/etc/network/interfaces"):
    interface = models.NetworkInterface(
        name="wlan0",
        dhcp=True,
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

    try:
        reload = subprocess.run(["/usr/sbin/ifreload", "-a"], capture_output=True)
        return reload.stdout
    except Exception as e:
        log.error(e.__str__())


def read_wlan_status() -> RfkillStatus:
    try:
        result = subprocess.run(["/usr/sbin/rfkill", "-J", "--output-all"], capture_output=True)
        result.check_returncode()
        json_data = result.stdout
        rfkill_data = json.loads(json_data)
        wlan_data = [v for k, v in rfkill_data.items()][0]
        wlan_data = [item for item in wlan_data if item['type'] == 'wlan']
        if len(wlan_data) == 0:
            raise Exception("No wlan detected")
        if len(wlan_data) > 1:
            raise Exception("More than one wlan detected")

        wlan_data = wlan_data[0]
        result = RfkillStatus(**wlan_data)
        return result

    except Exception as e:
        log.error(e.__str__())


def enable_wlan(device_id: int):
    try:
        result = subprocess.run(["/usr/sbin/rfkill", "unblock", f"{device_id}"], capture_output=True)
        result.check_returncode()
        log.info(f"Device {device_id} successfully unblocked")
        return result

    except Exception as e:
        log.error(e.__str__())


def disable_wlan(device_id: int):
    try:
        result = subprocess.run(["/usr/sbin/rfkill", "block", f"{device_id}"], capture_output=True)
        result.check_returncode()
        log.info(f"Device {device_id} successfully blocked")
        return result

    except Exception as e:
        log.error(e.__str__())
