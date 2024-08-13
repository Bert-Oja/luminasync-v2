"""
A module for CRUD operations on the Lamp model.
"""

from db.session import get_session
from db.models import Lamp


def create_lamp(ip, name):
    """
    Creates a new lamp object.
    Args:
        ip (str): The IP address of the lamp.
        name (str): The name of the lamp.
    Returns:
        Lamp: The created lamp object.
    """
    session = get_session()
    lamp = Lamp(ip=ip, name=name)
    session.add(lamp)
    session.commit()
    session.close()
    return lamp.to_dict()


def get_lamp_by_id(lamp_id):
    """
    Retrieves a lamp object by its ID.
    Args:
        lamp_id (int): The ID of the lamp.
    Returns:
        dict: A dictionary representation of the lamp object.
    """
    session = get_session()
    lamp = session.query(Lamp).filter_by(id=lamp_id).first()
    session.close()
    return lamp.to_dict() if lamp else None


def get_all_lamps():
    """
    Retrieves all lamp objects.
    Returns:
        list: A list of dictionary representations of the lamp objects.
    """
    session = get_session()
    lamps = session.query(Lamp).all()
    session.close()
    return [lamp.to_dict() for lamp in lamps]


def update_lamp(lamp_id, **kwargs):
    """
    Updates a lamp object.
    Args:
        lamp_id (int): The ID of the lamp.
        **kwargs: Arbitrary keyword arguments.
    Returns:
        dict: A dictionary representation of the updated lamp object.
    """
    session = get_session()
    lamp = session.query(Lamp).filter_by(id=lamp_id).first()
    if lamp:
        for key, value in kwargs.items():
            setattr(lamp, key, value)
        session.commit()
    session.close()
    return lamp.to_dict() if lamp else None


def delete_lamp(lamp_id):
    """
    Deletes a lamp object.
    Args:
        lamp_id (int): The ID of the lamp.
    """
    session = get_session()
    lamp = session.query(Lamp).filter_by(id=lamp_id).first()
    if lamp:
        session.delete(lamp)
        session.commit()
    session.close()
