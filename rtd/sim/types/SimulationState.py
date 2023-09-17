from enum import Enum
from functools import total_ordering



@total_ordering
class SimulationState(Enum):
    INVALID = 0
    CONSTRUCTED = 4
    SETTING_UP = 8
    SETUP_READY = 12
    INITIALIZING = 16
    READY = 20
    PRE_STEP = 24
    STEP = 28
    POST_STEP = 32
    COMPLETED = 36
    
    
    def __lt__(self, other: 'SimulationState'):
        if (self.__class__ == other.__class__):
            return self.value <= other.value
        return TypeError("LHS must be of type SimulationState")