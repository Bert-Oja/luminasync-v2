"""
A module for CRUD operations on the Lamp model.
"""

from typing import Any, Dict, List

from db.models import Lamp
from db.session import get_session


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


def get_lamp_by_ip(ip):
    """
    Retrieves a lamp object by its IP address.
    Args:
        ip (str): The IP address of the lamp.
    Returns:
        dict: A dictionary representation of the lamp object.
    """
    session = get_session()
    lamp = session.query(Lamp).filter_by(ip=ip).first()
    session.close()
    return lamp.to_dict() if lamp else None


def get_lamp_by_name(name):
    """
    Retrieves a lamp object by its name.
    Args:
        name (str): The name of the lamp.
    Returns:
        dict: A dictionary representation of the lamp object.
    """
    session = get_session()
    lamp = session.query(Lamp).filter_by(name=name).first()
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


def update_lamp(lamp_id, **kwargs) -> Dict[str, Any] | None:
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


def update_lamp_by_ip(ip, **kwargs) -> Dict[str, Any] | None:
    """
    Updates a lamp object by its IP address.

    Args:
        ip (str): The IP address of the lamp.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        dict: A dictionary representation of the updated lamp object.
    """
    session = get_session()
    try:
        lamp = session.query(Lamp).filter_by(ip=ip).first()
        if lamp:
            for key, value in kwargs.items():
                setattr(lamp, key, value)
            session.commit()  # Commit the session changes

            # The lamp object should not be expired because expire_on_commit=False
            return lamp.to_dict() if lamp else None
        else:
            return None
    except Exception as e:
        session.rollback()  # Roll back if there's an error
        raise e
    finally:
        session.close()  # Close the session


def update_lamps_in_batch(
    lamps_to_update: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Updates a batch of lamp objects.
    Args:
        lamps_to_update (list): A list of dictionaries containing lamp data.
    Returns:
        list: A list of dictionary representations of the updated lamp objects.
    """
    session = get_session()
    updated_lamps = []
    for lamp_data in lamps_to_update:
        lamp = session.query(Lamp).filter_by(id=lamp_data["ip"]).first()
        if lamp:
            for key, value in lamp_data.items():
                setattr(lamp, key, value)
            updated_lamps.append(lamp.to_dict())
    session.commit()
    session.close()
    return updated_lamps


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


# Non database functions
def turn_off_lamps():
    """
    Turns off all lamps.
    """
    session = get_session()
    lamps = session.query(Lamp).all()
    for lamp in lamps:
        lamp.is_on = False
    session.commit()
    session.close()
    return [lamp.to_dict() for lamp in lamps]
