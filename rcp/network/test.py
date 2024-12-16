import unittest
from unittest.mock import patch, MagicMock

from rcp import network

class TestNetwork(unittest.TestCase):
    def test_ifreload(self):
        result = network.reload_interfaces()

    @patch('subprocess.run')
    def test_read_wlan_status(self, mock_run):
        # Example JSON output from rfkill command
        example_output = """
{
   "": [
      {"id":0, "type":"wlan", "device":"phy0", "type-desc":"Wireless LAN", "soft":"unblocked", "hard":"unblocked"},
      {"id":1, "type":"bluetooth", "device":"hci0", "type-desc":"Bluetooth", "soft":"unblocked", "hard":"unblocked"}
   ]
}
"""

        # Mock the subprocess.run to return the example output
        mock_run.return_value = MagicMock(
            stdout=example_output.encode('utf-8'),
            returncode=0
        )

        from rcp.network import read_wlan_status
        from rcp.network.models import  RfkillStatus

        # Call the function to test
        result = read_wlan_status()

        # Check that the subprocess.run was called with the correct arguments
        mock_run.assert_called_with(["/usr/sbin/rfkill", "-J", "--output-all"], capture_output=True)

        # Check that the result is as expected
        expected_result = RfkillStatus(
            device="phy0",
            id=0,
            type="wlan",
            soft="unblocked",
            hard="unblocked"
        )
        self.assertEqual(result, expected_result)
