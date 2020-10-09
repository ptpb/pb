# common types that storage backends use to express state to views in a
# implementation-agnostic way

from enum import Enum, auto


__all__ = ["READ", "WRITE"]


PasteLabel = str

class READ(Enum):
    FOUND = auto()
    NOT_FOUND = auto()
    ERROR = auto()


class WRITE(Enum):
    CREATED = auto()
    ERROR = auto()
