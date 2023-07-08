from abc import ABCMeta, abstractmethod
from typing import Callable



class ReachSetInstance(metaclass=ABCMeta):
    '''
    Base class for a single reachable set generated for some state + parameters
    
    This is just an individual instance of a reachable set. It should
    hold the necessary information to make a nonlinear constraint. If a
    generated nonlinear constraint function is not atomic (specifically, if
    it can change class properties, the cache for the respective
    `ReachSetGenerator` should be disabled by setting `cache_max_size` to 0
    '''
    def __init__(self):
        # A tuple denoting the input minimum and maximums for the reachable
        # set on the left and right, respectively
        self.input_range: tuple[float, float] = None

        # The number of main shared parameters used by this set. Generally,
        # this should match the size of the final trajectory parameters
        self.num_parameters: int = None
    
    
    @abstractmethod
    def genNLConstraint(self, worldState) -> Callable:
        '''
        Generate the nonlinear constraint function for the provided worldState
        
        This function should handle the obstacle-frs pair or similar to
        generate the nonlinear constraint. This should return a function
        handle that return 4 outputs: (c, ceq, gc, gceq), where `c <= 0`
        and `ceq = 0` are the constraints, and `gc` and `gceq` are the
        gradients for the respective constraints
        
        Arguments:
            worldState: The observation of the world we want to generate the constraint for
        
        Returns:
            function_handle: A function handle for the generated nlconstraint where the
            constraint function's return type is (c, ceq, gc, gceq)
        '''
        pass