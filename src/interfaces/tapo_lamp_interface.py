"""
This module is an interface for the Tapo L530 lamp.
"""

from PyP100 import PyL530

from utils.color_translate import (hex_to_rgb, hsv_to_rgb, rgb_to_hex,
                                   rgb_to_hsv, tuple_to_rgb_string)


class TapoLampInterface:
    def __init__(self, lamp_ip: str, username: str, password: str):
        self.ip = lamp_ip
        self.bulb = PyL530.L530(lamp_ip, username, password)
        self.deviceProperties = self.getDeviceProperties()

    def _getStatus(self):
        return self.bulb.getDeviceInfo()

    def _getName(self):
        return self.bulb.getDeviceName()

    def _setBrightness(self, brightness):
        if brightness == 0:
            self.turnOff()
            return

        self.bulb.setBrightness(brightness)

    def getDeviceProperties(self):
        deviceProperties: dict = self._getStatus()
        brightness = deviceProperties.get("brightness")
        color_temp = deviceProperties.get("color_temp")
        hue_value = deviceProperties.get("hue") if color_temp == 0 else 0
        saturation = deviceProperties.get("saturation") if color_temp == 0 else 0
        rgb_value = hsv_to_rgb(hue_value, saturation, brightness)
        hex_value = rgb_to_hex(rgb_value)

        return {
            "name": self._getName(),
            "state": "On" if deviceProperties.get("device_on") else "Off",
            "color_temp": color_temp,
            "brightness": brightness,
            "hue": hue_value,
            "saturation": saturation,
            "rgb": tuple_to_rgb_string(rgb_value),
            "hex": hex_value,
        }

    def turnOn(self):
        self.bulb.turnOn()

    def turnOff(self):
        self.bulb.turnOff()

    def setColor(self, colorHex):
        rgb = hex_to_rgb(colorHex)
        hue, saturation, value = rgb_to_hsv(rgb)

        if self.deviceProperties["state"] == "Off":
            self.turnOn()
        self.bulb.setColor(hue, saturation)
        self._setBrightness(value)

    def setTemperature(self, temperature, brightness):
        self.bulb.setColorTemp(temperature)
        self._setBrightness(brightness)
