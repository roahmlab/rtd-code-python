from abc import ABCMeta, abstractmethod
from typing import Callable



class OptimizationEngine(metaclass=ABCMeta):
    '''
    Base class for any sort of nonlinear optimizer used
    '''
    @abstractmethod
    def performOptimization(self, initialGuess: list[float], objectiveCallback: Callable,
                            constraintCallback: Callable, bounds: dict) -> tuple[bool, float, float]:
        '''
        Use the given optimizer to perform the optimization
        
        Arguments:
            initialGuess: An initial guess vector used for the optimization. May not be the correct size and should be accounted for if not.
            objectiveCallback: A callback for the objective function of this specific optimization
            constraintCallback: A callback for the nonlinear constraints, where the return time is expected to be [c, ceq, gc, gceq].
            bounds: A dict containing input and output bounds.
        
        Returns:
            (success: bool, parameters: float, cost: double): `success`
            is if the optimization was successful or didn't time out.
            `parameters` are the trajectory parameters to use. `cost` is
            the final cost for the parameters found
        '''
        pass