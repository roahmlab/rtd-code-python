from abc import ABCMeta, abstractmethod
from typing import Callable
from rtd.entity.states import EntityState



class Objective(metaclass=ABCMeta):
    '''
    Base interface for creating the objective to optimize for the trajopt problem
    
    This should be extended and used to create an objective callback function
    for the optmization engine. Any necessary transformations or special
    function calls can take place inside the object
    '''
    @abstractmethod
    def genObjective(self, robotState: EntityState, waypoint, reachableSets: dict) -> Callable:
        '''
        Generate an objective callback for use with some optimizer
        
        Given the information, generate a handle for an objective
        function with return values `cost` and `grad_cost`
    
        Note:
            Any timeouts should be handled by the OptimizationEngine itself
        
        Arguments:
            robotState: Initial state of the robot
            waypoint: Some goal waypoint we want to get close to
            reachableSets: Instances of the relevant reachable sets
        
        Returns:
            function_handle: callback function of form 
            `def objectiveCallback(*params) -> [cost, grad_cost]`
        '''
        pass