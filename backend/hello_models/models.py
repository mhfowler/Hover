import datetime

from sqlalchemy import Column, Integer, String, \
    DateTime, ForeignKey, Boolean, Enum, UnicodeText, Table
from sqlalchemy.orm import relationship, backref

from hello_models.database import Base
from hello_webapp.extensions import db


class User(Base):
    """
    The main user object, used for authentication and for keeping track of user details
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=True)
    password = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    deleted = Column(Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
        }


class PasswordResetLink(Base):
    """
    This table is used to store singe-use tokens for password reset 
    """
    __tablename__ = 'resetlinks'
    reset_link_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    secret_link = Column(String(120), unique=True, nullable=False)
    expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


class TestObject(Base):
    """
    This object isn't necessary to the app.
    It's used by a helper route in helper_routes.py for convenience of confirming that 
    the server has a database connection
    """
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    key = Column(String(100))
    value = Column(String(100))

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<TestObject {}:{}>'.format(self.key, self.value)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
        }


class KeyVal(Base):
    """
    This object isn't necessary to the app.
    It's used by a helper route in helper_routes.py for convenience of confirming that 
    the server has a database connection
    """
    __tablename__ = 'keyval'
    id = Column(Integer, primary_key=True)
    key = Column(String(200))
    value = Column(String(200))

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
        }