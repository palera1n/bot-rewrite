from enum import IntEnum, unique, auto

@unique
class PermissionLevel(IntEnum):
    """Permission level enum"""
    
    EVERYONE = 0
    MEMPLUS = 1
    MEMPRO = 2
    HELPER = 3
    MOD = 4
    ADMIN = 5
    OWNER = 6


    # Checks
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

@unique
class Errors(IntEnum):
    """Error enum"""
    
    NO_PERMISSION = 0
    POINTS_UNDER_ZERO = 1
