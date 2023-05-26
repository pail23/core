"""Models for the mystrom integration."""
from dataclasses import dataclass

from pymystrom.bulb import MyStromBulb
from pymystrom.switch import MyStromSwitch


@dataclass
class MyStromData:
    """Data class for mystrom device data."""

    device: MyStromSwitch | MyStromBulb
    info: dict
