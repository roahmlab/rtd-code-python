from abc import ABCMeta, abstractmethod
from typing import Callable
from nptyping import NDArray, Shape, Float64

# type hinting
VolVec = NDArray[Shape['N,1'], Float64]



class OptimizationEngine(metaclass=ABCMeta):
    '''
    Base class for any sort of nonlinear optimizer used
    '''
    @abstractmethod
    def performOptimization(self, initialGuess: VolVec, objectiveCallback: Callable,
            constraintCallback: Callable, bounds: dict) -> tuple[bool, VolVec, float]:
        '''
        Use the given optimizer to perform the optimization
        RowVector
        Arguments:
            initialGuess: An initial guess ColVec used for the optimization. May not be the correct size and should be accounted for if not.
            objectiveCallback: A callback for the objective function of this specific optimization
            constraintCallback: A callback for the nonlinear constraints, where the return time is expected to be [c, ceq, gc, gceq].
            bounds: A dict containing input and output bounds
        
        Returns:
            (success: bool, parameters: ColVec, cost: float): `success`
            is if the optimization was successful or didn't time out.
            `parameters` are the trajectory parameters to use. `cost` is
            the final cost for the parameters found
        '''
        pass