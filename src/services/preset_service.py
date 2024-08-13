"""
A module for CRUD operations on the Preset model.
"""

from db.session import get_session
from db.models import Preset


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
