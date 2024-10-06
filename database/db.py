import json
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class ChatConfig(Base):
    __tablename__ = 'chat_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True, nullable=False)
    db_choice = Column(String, nullable=False)

class RaidConfig(Base):
    __tablename__ = 'raid_configs'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    raid_enabled = Column(Boolean, default=True)

Base.metadata.create_all(engine)

def add_user_to_db(user_ids, db_type):
    if db_type == 'lite':
        file_name = 'raiders.json'
    elif db_type == 'strong':
        file_name = 'kchat_raiders.json'
    else:
        added_lite = add_user_to_db(user_ids, 'lite')
        added_strong = add_user_to_db(user_ids, 'strong')
        return added_lite or added_strong

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    already_in_db = []
    added_users = []

    for user_id in user_ids:
        user_id_str = str(user_id)
        if user_id_str in data:
            already_in_db.append(user_id_str)
        else:
            data[user_id_str] = {
                "username": "No Username",
                "user_id": user_id
            }
            added_users.append(user_id_str)

    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

    return added_users, already_in_db

def remove_user_from_db(user_ids, db_type):
    if db_type == 'lite':
        file_name = 'raiders.json'
    elif db_type == 'strong':
        file_name = 'kchat_raiders.json'
    else:
        removed_lite = remove_user_from_db(user_ids, 'lite')
        removed_strong = remove_user_from_db(user_ids, 'strong')
        return removed_lite or removed_strong

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return [], user_ids

    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    not_in_db = []
    removed_users = []

    for user_id in user_ids:
        user_id_str = str(user_id)
        if user_id_str in data:
            del data[user_id_str]
            removed_users.append(user_id_str)
        else:
            not_in_db.append(user_id_str)

    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

    return removed_users, not_in_db