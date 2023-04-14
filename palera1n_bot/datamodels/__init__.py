from enum import IntEnum, unique, auto


@unique
class PermissionLevel(IntEnum):
    '''
    A Enum to store Permission Levels.
    '''
    EVERYONE = 0
    MEMPLUS = auto()
    MEMPRO = auto()
    HELPER = auto()
    MOD = auto()
    ADMIN = auto()
    OWNER = auto()

    # provide a default value for the enum
    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    # provide easy boolean checks

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __eq__(self, other):
        return self.value == other.value
