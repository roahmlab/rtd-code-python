from typing import NamedTuple



class TrajOptProps(NamedTuple):
    '''
    A NamedTuple for storing consistent properties we use across RTD
    for trajectory optimization. Can also be constructed with specific
    values rather than the default ones. Immutable
    '''
    
    # The time used for evaluation in the cost function
    timeForCost: float = 1.0

    # The time duration of the nominal plan. Braking action should
    # occur in horizonTime-planTime
    planTime: float = 0.5

    # The time of the overall trajectory until stop
    horizonTime: float = 1.0

    # Whether or not the timeout the optimization if it is taking too
    # long
    doTimeout: bool = False

    # The time at which the optimization should timeout
    timeoutTime: float = 0.5

    # Whether or not unknown or extra parameters (slack variables or if
    # no initial guess is given) should be randomized or zero
    # initialized
    randomInit: bool = False