from enum import Enum


class Lifetime(Enum):
    SINGLETON = 0
    TRANSIENT = 1
    _INTERNAL_DEFAULT = 2
