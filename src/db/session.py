"""
This module provides functions for working with
database sessions and seeding the database.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

from db.models import Base, Lamp, Preset

engine = create_engine("sqlite:///db/light_control.db")
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

Base.metadata.create_all(engine)


logger = logging.getLogger("LuminaSync")
_db_seeded = False


def get_session():
    """
    This function returns a session object.
    Returns:
        Session: A session object.
    """
    return Session()


def seed_db():
    """
    Seeds the database with Lamp and Preset objects if they do not already exist.
    """
    global _db_seeded
    if _db_seeded:
        logger.info("Database already seeded.")
        return
    try:
        session = get_session()

        # Seed Lamps
        lamp_ips = ["192.168.2.31", "192.168.2.32"]
        for ip in lamp_ips:
            existing_lamp = session.query(Lamp).filter_by(ip=ip).first()
            if not existing_lamp:
                logger.info(f"Adding Lamp with IP: {ip}")
                session.add(Lamp(ip=ip))
            else:
                logger.debug(f"Lamp with IP {ip} already exists.")

        # Seed Presets
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
        for preset_data in presets:
            existing_preset = (
                session.query(Preset).filter_by(name=preset_data["name"]).first()
            )
            if not existing_preset:
                logger.info(f"Adding Preset: {preset_data['name']}")
                session.add(
                    Preset(
                        name=preset_data["name"],
                        value=preset_data["value"],
                        protected=preset_data["protected"],
                    )
                )
            else:
                logger.debug(f"Preset {preset_data['name']} already exists.")

        session.commit()
        logger.info("Database seeding completed. How the hee-haw did you get here?")
        _db_seeded = True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"An error occurred while seeding the database: {e}")
    finally:
        session.close()
