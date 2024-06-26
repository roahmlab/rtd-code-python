from rtd.planner.trajopt import OptimizationEngine, TrajOptProps
from scipy.optimize import minimize
import numpy as np
from typing import Callable
from rtd.util.mixins.Typings import Vecnp



class ScipyOptimizationEngine(OptimizationEngine):
    '''
    Optimization Engine based on scipy.optimize.fsolve
    '''
    def __init__(self, trajOptProps: TrajOptProps, **options):
        # initialize base classes
        OptimizationEngine.__init__(self)
        # initialize other attributes
        self.trajOptProps: TrajOptProps = trajOptProps
    
    
    def performOptimization(self, initialGuess: Vecnp, objectiveCallback: Callable,
            constraintCallback: Callable, bounds: dict) -> tuple[bool, Vecnp, float]:
        '''
        Use scipy solve to perform the optimization
        
        Arguments:
            initialGuess: An initial guess Vecnp used for the optimization. May not be the correct size
            objectiveCallback: A callback for the objective function of this specific optimization
            constraintCallback: A callback for the nonlinear constraints, where the return time is expected to be [c, ceq, gc, gceq].
            bounds: A dict containing input and output bounds
        
        Returns:
            (success: bool, parameters: Vecnp, cost: float): `success`
            is if the optimization was successful or didn't time out.
            `parameters` are the trajectory parameters to use. `cost` is
            the final cost for the parameters found
        '''
        # how many extra variables we need
        n_remainder = np.size(bounds["param_limits"], 0) - len(initialGuess)
        # get bounds
        lb = bounds["param_limits"][:,0]
        ub = bounds["param_limits"][:,1]
        # generate random values if requested, otherwise zeros for any
        # thing not in our initial guess
        if self.trajOptProps.randomInit:
            initial_extra = np.random.uniform(lb[-n_remainder:], ub[-n_remainder:])
        else:
            initial_extra = np.zeros(n_remainder)
        
        # build initial guess
        initialGuess = np.concatenate((initialGuess, initial_extra))
        
        # optimization call
        ineqConstraint = lambda k: -constraintCallback(k)[0]
        eqConstraint = lambda k: constraintCallback(k)[1]
        ineqConstraintJac = lambda k: -constraintCallback(k)[2]
        eqConstraintJac = lambda k: constraintCallback(k)[3]
        
        result = minimize(
            fun=objectiveCallback,
            x0=initialGuess,
            method='SLSQP',
            #jac=True,   # use second return of fun as jacobean
            bounds=bounds["param_limits"],
            constraints = [
                {
                    "type": 'eq',
                    "fun": eqConstraint,
                    "jac": eqConstraintJac,
                },
                {
                    "type": 'ineq',
                    "fun": ineqConstraint,
                    "jac": ineqConstraintJac,
                },          
            ],
        )
        
        return (result.success, result.x, result.fun)