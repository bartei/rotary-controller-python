Network Connection
==================

Configure the WiFi connection for the Raspberry Pi.

## Fields

### Network Interface
The detected WiFi hardware adapter. If multiple adapters are
present, select the one you want to configure. The hardware
address and current state are shown below as read-only fields.

### Network (SSID)
Tap to open a popup listing available WiFi networks detected
by scanning. Select the network you want to connect to.

### Wifi Password
Enter the password for the selected network. For open networks,
leave this blank.

### Apply Configuration
Saves the network and password and attempts to connect. The
status area at the bottom shows connection progress and any errors.

## IP Properties

Once connected, the following are displayed (read-only):
- **IP Address** — assigned by DHCP or static configuration
- **DNS Server** — the DNS resolver in use
- **Default Gateway** — the network gateway

## Notes

- Network operations may take several seconds
- If connection fails, verify the password and try again
- Only WPA/WPA2/WPA3 personal networks are supported via this UI