import os
import sys
from unittest.mock import Mock, patch

# Add the project root to sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, src_path)

from src.interfaces.tapo_lamp_interface import TapoLampInterface  # noqa: E402


def test_tapo_lamp_interface_initialization():
    """Test initialization of TapoLampInterface."""
    with patch(
        "src.interfaces.tapo_lamp_interface.PyL530.L530"
    ) as mock_l530, patch.object(
        TapoLampInterface, "getDeviceProperties"
    ) as mock_get_props:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb
        mock_get_props.return_value = {}

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")

        # Assertions
        mock_l530.assert_called_with("192.168.1.100", "user", "pass")
        mock_get_props.assert_called_once()
        assert lamp_interface.ip == "192.168.1.100"
        assert lamp_interface.bulb == mock_bulb
        assert lamp_interface.deviceProperties == {}


def test_getDeviceProperties():
    """Test the getDeviceProperties method."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530, patch(
        "src.interfaces.tapo_lamp_interface.hsv_to_rgb"
    ) as mock_hsv_to_rgb, patch(
        "src.interfaces.tapo_lamp_interface.rgb_to_hex"
    ) as mock_rgb_to_hex, patch(
        "src.interfaces.tapo_lamp_interface.tuple_to_rgb_string"
    ) as mock_tuple_to_rgb_string:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        # Mock device info
        device_info = {
            "device_on": True,
            "brightness": 75,
            "color_temp": 0,
            "hue": 100,
            "saturation": 50,
        }
        mock_bulb.getDeviceInfo.return_value = device_info
        mock_bulb.getDeviceName.return_value = "Tapo Lamp"

        # Mock utility functions
        mock_hsv_to_rgb.return_value = (128, 64, 32)
        mock_rgb_to_hex.return_value = "#804020"
        mock_tuple_to_rgb_string.return_value = "128,64,32"

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")

        device_properties = lamp_interface.getDeviceProperties()

        # Assertions
        assert device_properties == {
            "name": "Tapo Lamp",
            "state": "On",
            "color_temp": 0,
            "brightness": 75,
            "hue": 100,
            "saturation": 50,
            "rgb": "128,64,32",
            "hex": "#804020",
        }

        mock_bulb.getDeviceInfo.assert_called_once()
        mock_bulb.getDeviceName.assert_called_once()
        mock_hsv_to_rgb.assert_called_with(100, 50, 75)
        mock_rgb_to_hex.assert_called_with((128, 64, 32))
        mock_tuple_to_rgb_string.assert_called_with((128, 64, 32))


def test_turnOn():
    """Test the turnOn method."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface.turnOn()

        mock_bulb.turnOn.assert_called_once()


def test_turnOff():
    """Test the turnOff method."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface.turnOff()

        mock_bulb.turnOff.assert_called_once()


def test_setColor():
    """Test the setColor method."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530, patch(
        "src.interfaces.tapo_lamp_interface.hex_to_rgb"
    ) as mock_hex_to_rgb, patch(
        "src.interfaces.tapo_lamp_interface.rgb_to_hsv"
    ) as mock_rgb_to_hsv:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        # Mock utility functions
        mock_hex_to_rgb.return_value = (128, 64, 32)
        mock_rgb_to_hsv.return_value = (100, 50, 75)

        # Mock device properties
        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface.deviceProperties = {"state": "Off"}

        lamp_interface.setColor("#804020")

        mock_hex_to_rgb.assert_called_with("#804020")
        mock_rgb_to_hsv.assert_called_with((128, 64, 32))

        mock_bulb.turnOn.assert_called_once()
        mock_bulb.setColor.assert_called_with(100, 50)
        mock_bulb.setBrightness.assert_called_with(75)


def test_setTemperature():
    """Test the setTemperature method."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface.setTemperature(4000, 80)

        mock_bulb.setColorTemp.assert_called_with(4000)
        mock_bulb.setBrightness.assert_called_with(80)


def test__setBrightness_zero():
    """Test the _setBrightness method when brightness is zero."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface._setBrightness(0)

        mock_bulb.turnOff.assert_called_once()
        mock_bulb.setBrightness.assert_not_called()


def test__setBrightness_non_zero():
    """Test the _setBrightness method when brightness is non-zero."""
    with patch("src.interfaces.tapo_lamp_interface.PyL530.L530") as mock_l530:
        mock_bulb = Mock()
        mock_l530.return_value = mock_bulb

        lamp_interface = TapoLampInterface("192.168.1.100", "user", "pass")
        lamp_interface._setBrightness(75)

        mock_bulb.setBrightness.assert_called_with(75)
        mock_bulb.turnOff.assert_not_called()
