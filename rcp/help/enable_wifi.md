Enable Wifi
===========

Turns the WiFi radio on or off on the Raspberry Pi.

## Behavior

- **ON:** The WiFi adapter is enabled and can connect to networks.
  The network interface dropdown and connection fields become active.
- **OFF:** The WiFi adapter is disabled. This saves power and
  avoids unintended network connections in secure environments.

## Notes

- Requires a compatible WiFi adapter (built-in on Raspberry Pi 3/4/5)
- Changes take effect immediately via nmcli
- If WiFi was previously connected, disabling and re-enabling will
  attempt to reconnect to the last known network