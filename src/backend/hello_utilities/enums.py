from enum import Enum


class UserType(Enum):
    """
    different types users can have
    """
    DEFAULT = 'default'
    ADMIN = 'admin'
    SUPERADMIN = 'superadmin'