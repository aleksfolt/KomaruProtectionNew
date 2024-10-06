from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatConfig(Base):
    __tablename__ = 'chat_configs'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    db_choice = Column(String, nullable=False)

class RaidConfig(Base):
    __tablename__ = 'raid_configs'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    raid_enabled = Column(Boolean, default=True)