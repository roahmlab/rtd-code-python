from abc import ABCMeta, abstractmethod
from rtd.entity.states import EntityState
from rtd.planner.trajectory import Trajectory
from rtd.sim.world import WorldState



class RtdPlanner(metaclass=ABCMeta):
    '''
    This class specifies the overall planner
    
    It should set up anything for any special type of RTD planner.
    Construction of a special version of this should do the following:
    
    - Construct OptimizationEngine(s) with parameters
    - Construct ReachableSets for each reachable set and trajectory type
    - Construct some Objective object for the problem at hand
    - Determine/set RtdTrajOpt parameters and create it for each trajectory type
    
    Then on each waypoint, we call for a trajectory plan using
    `planTrajectory`. That will use RTD to solve for a trajectory
    '''
    @abstractmethod
    def planTrajectory(self, robotState: EntityState, worldState: WorldState, waypoint) -> Trajectory | None:
        '''
        Generate a trajectory for the given states and waypoint.
        
        Loops over each RtdTrajOpt instance (thus, each trajectory type)
        with the given RobotState, WorldState, Waypoint, and initial guess
        if wanted
        
        From the results, this should select the best valid Trajectory.
        Otherwise it should return an empty or invalid trajectory which
        will throw when attempting to set the new trajectory, ensuring
        the old one continues - or something like that.
        
        Arguments:
            robotState: EntityState: Current state of the robot
            worldState: WorldState: Current state of the world
            waypoint: The waypoint to consider for the trajopt problem(s)
        
        Returns:
            Trajectory or None: A trajectory object, which may or may not be
            valid. If no plans are found, this may alternately return an
            empty value.
        '''
        pass