from typing import Callable
from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetInstance
from rtd.planner.trajopt import Objective, TrajOptProps
from rtd.planner.trajectory import TrajectoryFactory, Trajectory
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class GenericArmObjective(Objective):
    def __init__(self, trajOptProps: TrajOptProps, trajectoryFactory: TrajectoryFactory):
        '''
        Constructs this objective function generator.
        Provide a trajectory factory object which creates unique
        trajectory objects with each call and the properties of the
        overall trajopt problem, from which the time for the cost is
        used with some trajectory to create the objective
    
        Arguments:
            trajOptProps: TrajOptProps
            trajectoryFactory: TrajectoryFactory
        '''
        # initialize base classes
        Objective.__init__(self)
        # set properties
        self.trajectoryFactory = trajectoryFactory
        self.t_cost = trajOptProps.timeForCost

    
    def genObjective(self, robotState: EntityState, waypoint, reachableSets: dict[str, ReachSetInstance]) -> Callable:
        q_des = waypoint
        
        # create an trajectory instance for whatever generic trajectory
        # factory we were given
        trajectoryObj = self.trajectoryFactory.createTrajectory(robotState, reachableSets)
        
        # create and return the function handle
        return lambda trajectoryParams: self.evalTrajectory(trajectoryParams, trajectoryObj, q_des, robotState.time + self.t_cost)
    
    
    @staticmethod
    def evalTrajectory(trajectoryParams: RowVec, trajectoryObj: Trajectory, q_des, t_cost: float | RowVec) -> float:
        '''
        Helper function purely accessible to this class without any class state
        which a handle can be made to to evaluate the trajectory for the cost.
        Should work for any generic arm trajectory in joint space
        '''
        trajectoryObj.setParameters(trajectoryParams)
        plan = trajectoryObj.getCommand(t_cost)
        return np.sum(np.power(plan.q_des - q_des, 2))