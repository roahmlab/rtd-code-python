from rtd.planner.trajopt import TrajOptProps, Objective, OptimizationEngine
from rtd.planner.trajectory import TrajectoryFactory
from rtd.sim.world import WorldEntity
from rtd.entity.states import EntityState
from rtd.planner.trajectory import Trajectory
import numpy as np
from numpy.typing import NDArray

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class RtdTrajOpt:
    '''
    Core trajectory optimization routine for RTD
    
    This object handles the necessary calls to perform the actual trajectory
    optimization when requested. It calls the generators for the reachble
    sets and combines all the resulting nonlinear constraints in the end
    '''
    def __init__(self, trajOptProps: TrajOptProps, robot: WorldEntity, reachableSets: dict,
                 objective: Objective, optimizationEngine: OptimizationEngine,
                 trajectoryFactory: TrajectoryFactory, **options):
        '''
        Construct the RtdTrajOpt object.
        
        Store all the handles to objects that we want to use.
        This should encapsulate the main trajectory optimization
        aspection of RTD & ideally need very little specialization
        between versions
        
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
                     initialGuess: Trajectory, **rsAdditionalArgs: dict[dict]) -> tuple[Trajectory, float, dict]:
        '''
        Execute the solver for trajectory optimization
        
        Note:
            The returned `info` dict has the following entries:
            worldState, robotState, rsInstances, nlconCallbacks,
            objectiveCallback, waypoint, bounds, num_parameters, guess,
            trajectory, cost
        
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
        # generate reachable set
        logger.info("Generating reachable sets and nonlinear constraints")
        rsInstances_arr = dict()
        
        for rs_name in self.reachableSets:
            logger.debug(f"Generating {rs_name}")
            
            # get additional arguments for current reachset
            rs_args = dict()
            if rs_name in rsAdditionalArgs:
                logger.debug(f"Passing additional arguments to generate {rs_name}")
                rs_args = rsAdditionalArgs[rs_name]
            
            # generate reachset
            rs_dict = self.reachableSets[rs_name].getReachableSet(robotState, **rs_args, ignore_cache=False)
            
            # ???
            for idx in range(len(rs_dict)):
                rsInstances_arr[idx] = {
                    'id': rs_dict[idx]["id"],
                    'rs': {rs_name: rs_dict[idx]["rs"]},
                }
                rsInstances_arr[idx]["num_instances"] = len(rsInstances_arr[idx]["rs"])
            
            # generate nonlinear constraints 
                

    class merge_constraints:
        '''
        A functor for computing the constraints
        for a given input, with lookup for speed
        optimizations
        '''
        def __init__(self, nlconCallback, nlconNames, buffer_size=16):
            self.buffer = list()
            self.buffer_size = buffer_size
        
        
        def __call__(self, k):
            '''
            Overload call to work as a functor
            '''
            if ((res:=self.findBuffer(k)) != None):
                return res
            
            # do some calculation
            res = tuple()
            self.updateBuffer(k, res)
            return res
        
        
        def updateBuffer(self, k, res):
            '''
            Ensure buffer size < buffer_size and add
            input-output pair into buffer
            '''
            if len(self.buffer) > self.buffer_size:
                self.buffer.pop(0)
                self.buffer.append((k, res))
            else:
                self.buffer.append((k, res))
        
        
        def findBuffer(self, k) -> tuple | None:
            '''
            Return output if result for given input
            exists in the buffer, otherwise return
            None
            '''
            for i in self.buffer:
                if i[0] == k:
                    return i[1]
            return None