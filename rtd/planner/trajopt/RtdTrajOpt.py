from rtd.planner.trajopt import TrajOptProps, Objective, OptimizationEngine
from rtd.planner.trajectory import TrajectoryFactory
from rtd.sim.world import WorldEntity
from rtd.entity.states import EntityState
from rtd.planner.trajectory import Trajectory
import numpy as np
from numpy.typing import NDArray



class RtdTrajOpt:
    '''
    Core trajectory optimization routine for RTD
    
    This object handles the necessary calls to perform the actual trajectory
    optimization when requested. It calls the generators for the reachble
    sets and combines all the resulting nonlinear constraints in the end.
    '''
    def __init__(self, trajOptProps: TrajOptProps, robot: WorldEntity, reachableSets: dict,
                 objective: Objective, optimizationEngine: OptimizationEngine,
                 trajectoryFactory: TrajectoryFactory, **options):
        '''
        Construct the RtdTrajOpt object.
        
        Store all the handles to objects that we want to use.
        This should encapsulate the main trajectory optimization
        aspection of RTD & ideally need very little specialization
        between versions.
        
        Arguments:
            trajOptProps: TrajOptProps
            robot (rtd.sim.world.WorldEntity)
            reachableSets (struct)
            objective (rtd.planner.trajopt.Objective)
            optimizationEngine (rtd.planner.trajopt.OptimizationEngine)
            trajectoryFactory (rtd.planner.trajectory.TrajectoryFactory)
        '''
        self.trajOptProps: TrajOptProps = None
        self.robot: WorldEntity = robot
        self.reachableSets: dict = reachableSets
        self.objective: Objective = objective
        self.optimizationEngine: OptimizationEngine = optimizationEngine
        self.trajectoryFactory: TrajectoryFactory = trajectoryFactory
    
    
    def solveTrajOpt(self, robotState: EntityState, worldState, waypoint,
                     initialGuess: Trajectory, **rsAdditionalArgs) -> tuple[Trajectory, float, dict]:
        '''
        Execute the solver for trajectory optimization.
        
        Note:
            The returned `info` dict has the following entries:
            worldState, robotState, rsInstances, nlconCallbacks,
            objectiveCallback, waypoint, bounds, num_parameters, guess,
            trajectory, cost.
        
        Arguments:
            robotState: EntityState: State of the robot.
            worldState: Observed state of the world for the reachable sets
            waypoint: Waypoint we want to optimize to
            initialGuess: Trajectory: Past trajectory to use as an initial guess
            rsAdditionalArgs: additional arguments to pass to the reachable sets, by set name
        
        Returns:
            (trajectory: Trajectory, cost: float, info: dict):
            `trajectory` is an instance of the trajectory object that
            corresponds to the solved trajectory optimization. If it
            wasn't successful, this will either be an invalid
            trajectory or empty. `cost` is the final cost of the
            objective used. `info` is a dict of optimization data.
        '''
        pass