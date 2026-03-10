Software Update
===============

Manage application updates directly from the DRO interface.

## Fields

### Currently Installed Release
Shows the version currently running. This is read-only.

### Refresh Available Releases
Fetches the latest release list from GitHub. Requires an active
internet connection.

### Allow Installation of Experimental Versions
When enabled, pre-release and development builds appear in the
available releases list. These may contain new features but are
less tested.

- **OFF (default):** Only stable, tagged releases are shown.
- **ON:** Includes "dev (experimental)" and release candidates.

### Available Releases
A dropdown of versions available for installation. Select the
desired version before clicking Install.

### Install Selected Release
Downloads and installs the selected version. The application
will need to be restarted after installation.

## Notes

- Requires an internet connection to fetch and install updates
- The update process may take a few minutes depending on your
  connection speed
- Installation progress and any errors are shown in the status
  area below
- Use "Exit Application" to restart after a successful update