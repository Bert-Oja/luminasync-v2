"""
A module for CRUD operations on the Preset model.
"""

import os

from dotenv import load_dotenv

from db.models import Preset
from db.session import get_session
from interfaces.tapo_lamp_interface import TapoLampInterface
from services.lamp_service import get_all_lamps
from services.lamp_service import update_lamp_by_ip as update_lamp


def create_preset(name, value):
    """
    Creates a new preset object.
    Args:
        name (str): The name of the preset.
        value (dict): The value of the preset.
    Returns:
        dict: A dictionary representation of the created preset object.
    """
    session = get_session()
    preset = Preset(name=name, value=value)
    session.add(preset)
    session.commit()
    session.close()
    return preset.to_dict()


def get_preset_by_id(preset_id):
    """
    Retrieves a preset object by its ID.
    Args:
        preset_id (int): The ID of the preset.
    Returns:
        dict: A dictionary representation of the preset object.
    """
    session = get_session()
    preset = session.query(Preset).filter_by(id=preset_id).first()
    session.close()
    return preset.to_dict() if preset else None


def get_all_presets():
    """
    Retrieves all preset objects.
    Returns:
        list: A list of dictionary representations of the preset objects.
    """
    session = get_session()
    presets = session.query(Preset).all()
    session.close()
    return [preset.to_dict() for preset in presets]


def update_preset(preset_id, **kwargs):
    """
    Updates a preset object.
    Args:
        preset_id (int): The ID of the preset.
        **kwargs: Arbitrary keyword arguments.
    Returns:
        dict: A dictionary representation of the updated preset object.
    """
    session = get_session()
    preset = session.query(Preset).filter_by(id=preset_id).first()
    for key, value in kwargs.items():
        setattr(preset, key, value)
    session.commit()
    session.close()
    return preset.to_dict()


def delete_preset(preset_id):
    """
    Deletes a preset object.
    Args:
        preset_id (int): The ID of the preset.
    """
    session = get_session()
    preset = session.query(Preset).filter_by(id=preset_id).first()
    session.delete(preset)
    session.commit()
    session.close()


def bulk_insert_presets(presets):
    """
    Inserts multiple presets into the database.
    Args:
        presets (list): A list of dictionaries representing presets.
    """
    session = get_session()
    for preset in presets:
        session.add(Preset(name=preset["name"], value=preset["value"]))
    session.commit()
    session.close()


# Non database interaction functions


class PresetException(Exception):
    pass


def apply_preset(value: list | dict, available_lights: list):
    """
    Applies a preset value.
    Args:
        value (list | dict): The value of the preset.
        available_lights (list): A list of available lights.
    """
    try:
        load_dotenv()
        bulbs = [
            TapoLampInterface(
                lamp.ip, os.getenv("TAPO_USERNAME"), os.getenv("TAPO_PASSWORD")
            )
            for lamp in available_lights
        ]
        if isinstance(value, dict):
            # Handle a single setting object
            apply_setting_to_bulb(value, bulbs)
        elif isinstance(value, list):
            # Handle multiple settings in an array
            for setting, bulb in zip(value, bulbs):
                apply_setting_to_bulb(setting, bulb)

        lamps_data = get_all_lamps()
        return {  # Return an object containing the id, hex and brightness of each lamp
            lamp["id"]: {
                "id": lamp["id"],
                "hex": lamp["hex"],
                "brightness": lamp["brightness"],
                "rgb": lamp["rgb"],
            }
            for lamp in lamps_data
        }
    except Exception as e:
        raise PresetException(f"Failed to apply preset: {e}") from e


def apply_setting_to_bulb(
    setting: dict, bulb: list[TapoLampInterface] | TapoLampInterface
):
    """
    Apply a single setting to the bulbs.
    If bulbs is a list, apply to all. If it's a single bulb, apply to that one.

    Args:
        setting (dict): The setting to apply to the bulbs.
        bulbs (list[TapoLampInterface] | TapoLampInterface): The bulbs to apply the setting to.

    Returns:
        None
    """
    if isinstance(bulb, list):
        for b in bulb:
            apply_setting_to_bulb(setting, b)
        return

    if setting["type"] == "color":
        bulb.setColor(setting["setting"])
    elif setting["type"] == "temp":
        bulb.setTemperature(setting["setting"], setting["brightness"])

    update_lamp(bulb.ip, **bulb.getDeviceProperties())


def turn_off_bulbs():
    """
    Turns off all bulbs.
    """
    bulbs = [
        TapoLampInterface(
            lamp["ip"], os.getenv("TAPO_USERNAME"), os.getenv("TAPO_PASSWORD")
        )
        for lamp in get_all_lamps()
    ]
    for bulb in bulbs:
        bulb.turnOff()
        update_lamp(bulb.ip, **bulb.getDeviceProperties())

    return True
