from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Preset(Base):
    __tablename__ = 'presets'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    settings = Column(String)

def init_db():
    engine = create_engine('sqlite:///light_control.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def save_preset(preset):
    session = init_db()
    new_preset = Preset(name=preset['name'], settings=preset['settings'])
    session.add(new_preset)
    session.commit()

def get_preset(name):
    session = init_db()
    return session.query(Preset).filter_by(name=name).first()
