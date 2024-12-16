import asyncio
import threading

import logging
import subprocess
import time
from typing import List, Tuple, Iterable

import sdbus

from sdbus_block.networkmanager import (
    NetworkConnectionSettings,
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    NetworkManager,
    NetworkManagerSettings,
    IPv4Config
)
from sdbus_block.networkmanager.enums import DeviceType, DeviceState

from sdbus_block.networkmanager.settings import ConnectionProfile, ConnectionSettings, WirelessSettings, \
    WirelessSecuritySettings

sdbus.set_default_bus(sdbus.sd_bus_open_system())
log = logging.getLogger(__file__)


def find_our_connection():
    nms = NetworkManagerSettings()

    connections = nms.list_connections()
    profiles = [NetworkConnectionSettings(item).get_profile() for item in connections]

    # search for our own profile
    wlan_profiles = [item for item in profiles if item.connection.connection_id == "ospi"]

    if len(wlan_profiles) == 1:
        return wlan_profiles[0]
    else:
        return None


def get_all_network_interface_names(
        types_filter: Iterable[DeviceType] = (DeviceType.WIFI,)
) -> List[str]:
    network_manager = NetworkManager()
    all_devices = {path: NetworkDeviceGeneric(path) for path in network_manager.devices}

    # Get only ethernet and wifi devices
    filtered_devices = {
        k: v for k, v in all_devices.items() if v.device_type in types_filter
    }

    # get the ifname form the devices
    names = [item.interface for item in filtered_devices.values()]
    return names


def get_profile_by_id(profile_id: str = "ospi") -> ConnectionProfile or None:
    nms = NetworkManagerSettings()
    connections = nms.list_connections()
    profiles = []
    for item in connections:
        try:
            profile = NetworkConnectionSettings(item).get_profile()
            profiles.append(profile)
        except Exception as e:
            log.error(e.__str__())

    wlan_profiles = [item for item in profiles if item.connection.connection_id == profile_id]

    if len(wlan_profiles) == 1:
        return wlan_profiles[0]
    else:
        return None


def get_psk(profile: ConnectionProfile) -> str:
    if profile is None:
        return ""
    else:
        return profile.wireless_security.psk


def get_ssid(profile: ConnectionProfile) -> str:
    if profile is None:
        return ""
    else:
        return profile.wireless.ssid.decode("UTF-8")


def get_connection_method(profile: ConnectionProfile) -> str:
    if profile is None:
        return ""
    else:
        return profile.ipv4.method


def get_connection_by_profile(profile:  ConnectionProfile):
    if profile is None:
        return None
    else:
        nms = NetworkManagerSettings()
        connections = nms.get_connections_by_id(profile.connection.connection_id)
        if len(connections) != 1:
            raise ValueError("Unable to find the connection associated with the given profile")
        return connections[0]


def get_ipv4(profile: ConnectionProfile) -> Tuple:
    if profile is None:
        return "", "", ""

    network_manager = NetworkManager()
    interface_name = profile.connection.interface_name
    device_path = network_manager.get_device_by_ip_iface(interface_name)

    generic_device = NetworkDeviceGeneric(device_path)
    print('Device: ', generic_device.interface)
    device_ip4_conf_path = generic_device.ip4_config
    if device_ip4_conf_path == '/':
        return "", "", ""
    else:
        ip4_conf = IPv4Config(device_ip4_conf_path)
        if len(ip4_conf.address_data) != 1:
            return "", "", ""
        first_address = ip4_conf.address_data[0]
        gateway = ip4_conf.gateway
        address = first_address['address'][1]
        netmask = str(first_address['prefix'][1])
        return address, netmask, gateway


def enable_wifi():
    """Enables Wi-Fi on Linux."""
    try:
        result = subprocess.run("nmcli radio wifi on", shell=True)
        if result.returncode:
            log.error("Failed to enable Wi-Fi")
        else:
            log.info("Wi-Fi has been enabled.")

        return result.returncode == 0
    except Exception as error:
        log.exception(error.__str__())


def disable_wifi():
    """Enables Wi-Fi on Linux."""
    try:
        result = subprocess.run("nmcli radio wifi off", shell=True)
        if result.returncode:
            log.error("Failed to disable Wi-Fi")
        else:
            log.info("Wi-Fi has been disabled.")
        return result.returncode == 0
    except Exception as error:
        log.exception(error.__str__())


def activate_connection(profile: ConnectionProfile):
    enable_wifi()
    interface_name = profile.connection.interface_name

    network_manager = NetworkManager()
    device = network_manager.get_device_by_ip_iface(interface_name)
    connection = get_connection_by_profile(profile)

    network_manager.activate_connection(connection=connection, device=device)
    network_device = NetworkDeviceWireless(device)
    network_device.state: DeviceState
    return network_manager.activate_connection(connection=connection)


def deactivate_connection(profile: ConnectionProfile):
    disable_wifi()
    network_manager = NetworkManager()
    connection = get_connection_by_profile(profile)
    return network_manager.deactivate_connection(active_connection=connection)


def get_connection_ssid(profile_id: str) -> str or None:
    profile = get_profile_by_id(profile_id)
    if profile is None:
        return None
    return profile.wireless.ssid


def get_connection_psk(profile_id: str) -> str or None:
    profile = get_profile_by_id(profile_id)
    if profile is None:
        return None
    return profile.wireless_security.psk


def create_new_connection_profile(ssid: str, psk: str):
    sdbus.set_default_bus(sdbus.sd_bus_open_system())
    network_manager = NetworkManager()

    profile = ConnectionProfile(
        connection=ConnectionSettings(
            connection_id="ospi",
            connection_type="802-11-wireless",
            interface_name="wlo1",
            # interface_name="wlan0",
        ),
        wireless=WirelessSettings(
            ssid=ssid.encode("UTF-8")
        ),
        wireless_security=WirelessSecuritySettings(
            key_mgmt="wpa-psk",
            psk=psk
        )
    )

    result = network_manager.add_and_activate_connection_profile(profile)
    result


def update_connection_profile(connection_profile: ConnectionProfile, ssid: str, psk: str):
    connection_profile.wireless.ssid = ssid
    connection_profile.wireless_security.psk = psk

