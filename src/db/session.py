"""
This module provides functions for working with 
database sessions and seeding the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db.models import Base, Lamp, Preset

engine = create_engine("sqlite:///db/light_control.db")
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

Base.metadata.create_all(engine)


def get_session():
    """
    This function returns a session object.
    Returns:
        Session: A session object.
    """
    return Session()


def seed_db():
    """
    Seeds the database with Lamp objects if the Lamp table is empty.

    Lamp objects are created with predefined IP addresses.
    """
    session = get_session()
    if session.query(Lamp).first() is None:  # Corrected query method
        lamp_ips = ["192.168.2.31", "192.168.2.32"]
        for ip in lamp_ips:
            session.add(Lamp(ip=ip))
        session.commit()

    if session.query(Preset).first() is None:  # Corrected query method
        presets = [
            {
                "name": "default",
                "value": {"type": "temp", "setting": 3500, "brightness": 80},
                "protected": 1,
            },
            {
                "name": "meeting",
                "value": {"type": "temp", "setting": 5000, "brightness": 100},
                "protected": 1,
            },
        ]
        for preset in presets:
            session.add(
                Preset(
                    name=preset["name"],
                    value=preset["value"],
                    protected=preset["protected"],
                )
            )
        session.commit()
    session.close()

    return
