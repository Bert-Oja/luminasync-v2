"""
A module for the database models.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Base model for database models.
    Attributes:
        id (int): The primary key of the model.
        updated_at (datetime): The timestamp of when the model was last updated.
    """

    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Preset(BaseModel):
    """
    Preset model for storing preset data.
    Attributes:
        name (str): The name of the preset.
        value (dict): The value of the preset
    """

    __tablename__ = "presets"
    name = Column(String, unique=True, nullable=False)
    value = Column(JSON, nullable=False)

    def to_dict(self):
        """
        Returns the preset as a dictionary.
        """
        return {
            "id": str(self.id),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name": self.name,
            "value": self.value,
        }


class Lamp(BaseModel):
    """
    Lamp model for storing lamp data.
    Attributes:
        ip (str): The IP address of the lamp.
        name (str): The name of the lamp.
        state (str): The state of the lamp (on/off).
        color_temp (int): The color temperature of the lamp.
        brightness (int): The brightness of the lamp.
        hue (int): The hue of the lamp.
        saturation (int): The saturation of the lamp.
        rgb (str): The RGB color of the lamp.
        hex (str): The hex color
    """

    __tablename__ = "lamps"
    ip = Column(String(50), nullable=False)
    name = Column(String(50))
    state = Column(String(3))
    color_temp = Column(Integer)
    brightness = Column(Integer)
    hue = Column(Integer)
    saturation = Column(Integer)
    rgb = Column(String(50))
    hex = Column(String(50))

    def to_dict(self):
        """
        Returns the lamp as a dictionary.
        """
        return {
            "id": str(self.id),
            "ip": self.ip,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name": self.name,
            "state": self.state,
            "color_temp": self.color_temp,
            "brightness": self.brightness,
            "hue": self.hue,
            "saturation": self.saturation,
            "rgb": self.rgb,
            "hex": self.hex,
        }
