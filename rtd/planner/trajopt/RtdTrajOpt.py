from rtd.planner.trajopt import TrajOptProps, Objective, OptimizationEngine
from rtd.planner.trajectory import TrajectoryFactory
from rtd.planner.reachsets import ReachSetGenerator
from rtd.sim.world import WorldEntity, WorldState
from rtd.entity.states import EntityState
from rtd.planner.trajectory import Trajectory
from rtd.planner.reachsets import ReachSetInstance
import numpy as np
from typing import Callable
from nptyping import NDArray, Shape, Float64

# define top level module logger
import logging
logger = logging.getLogger(__name__)

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class RtdTrajOpt:
    '''
    Core trajectory optimization routine for RTD
    
    This object handles the necessary calls to perform the actual trajectory
    optimization when requested. It calls the generators for the reachble
    sets and combines all the resulting nonlinear constraints in the end
    '''
    def __init__(self, trajOptProps: TrajOptProps, robot: WorldEntity,
                 reachableSets: dict[str, ReachSetGenerator],
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
            robot: WorldEntity
            reachableSets: dict[str, ReachSetGenerator]
            objective: Objective
            optimizationEngine: OptimizationEngine
            trajectoryFactory: TrajectoryFactory
        '''
        self.trajOptProps: TrajOptProps = trajOptProps
        self.robot: WorldEntity = robot
        self.reachableSets: dict[str, ReachSetGenerator] = reachableSets
        self.objective: Objective = objective
        self.optimizationEngine: OptimizationEngine = optimizationEngine
        self.trajectoryFactory: TrajectoryFactory = trajectoryFactory
    
    
    def solveTrajOpt(self, robotState: EntityState, worldState: WorldState, waypoint,
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
            worldState: WorldState: Observed state of the world for the reachable sets
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
        rsInstances_dict: dict[int, dict[str, ReachSetInstance]] = dict()
        
        for (rs_name, rs_gen) in self.reachableSets.items():
            logger.debug(f"Generating {rs_name}")
            
            # get additional arguments for current reachset
            rs_args = dict()
            if rs_name in rsAdditionalArgs:
                logger.debug(f"Passing additional arguments to generate {rs_name}")
                rs_args = rsAdditionalArgs[rs_name]
            
            # generate reachset
            rsInstances = rs_gen.getReachableSet(robotState, ignore_cache=False, **rs_args)
            
            # save in rsInstances
            for (rs_id, rs) in rsInstances.items():
                if rs_id not in rsInstances_dict:
                    rsInstances_dict[rs_id] = dict()
                rsInstances_dict[rs_id][rs_name] = rs
            
            
        # generate nonlinear constraints
        successes: dict[int, bool] = dict()
        parameters: dict[int, RowVec] = dict()
        costs: dict[int, float] = dict()
        
        for (rs_id, rsInstances) in rsInstances_dict.items():
            logger.info(f"Solving problem {rs_id}")
            logger.debug("Generating nonlinear constraints")
            nlconCallbacks = {rs_name: rs.genNLConstraint(worldState) for (rs_name, rs) in rsInstances}
            
            # validate that rs sizes are all equal
            logger.debug("Validating sizes")
            num_parameters = {rs.num_parameters for rs in rsInstances.values()}
            if len(num_parameters) != 1:
                raise Exception("Reachable set parameter sizes don't match!")
            # get num_parameters[0] from num_parameters={num_parameters}
            for n_params in num_parameters:
                num_parameters = n_params
            
            # compute bounds
            logger.debug("Computing bounds")
            param_bounds = np.ones((num_parameters, 2)) * (-np.inf, np.inf)
            for rs in rsInstances.values():
                new_bounds = np.tile(rs.input_range, (num_parameters, 1))
                # Ensure bounds are the intersect of the intervals for the
                # parameters
                param_bounds[:,0] = np.maximum(param_bounds[:,0], new_bounds[:,0])
                param_bounds[:,1] = np.minimum(param_bounds[:,1], new_bounds[:,1])
            
            # combine nlconCallbacks
            constraintCallback = self.merge_constraints(nlconCallbacks)
            
            # create bounds
            bounds = {
                'param_limits': param_bounds,
                'output_limits': list()
            }
            
            # create the objective
            objectiveCallback = self.objective.genObjective(robotState, waypoint, rsInstances)
            
            # if initial guess is none or invalid, make zero
            try:
                guess = initialGuess.trajectoryParams()
            except Exception:
                guess = list()
            
            # optimize
            logger.info("Optimizing!")
            success, parameter, cost = self.optimizationEngine.performOptimization(
                guess, objectiveCallback, constraintCallback, bounds)

            successes[rs_id] = success
            parameters[rs_id] = parameter
            costs[rs_id] = cost
        
        # select the best cost
        min_cost = np.inf
        min_idx = -1
        for rs_id in rsInstances_dict:
            if successes[rs_id] and costs[rs_id]<min_cost:
                min_cost = costs[rs_id]
                min_idx = rs_id
        
        # if success
        if min_idx != -1:
            logger.info(f"Optimal solution found in problem {min_idx}")
            rsInstances = rsInstances_dict[min_idx]
            parameter = parameters[min_idx]
            trajectory = self.trajectoryFactory.createTrajectory(robotState, rsInstances, parameter)
        else:
            trajectory = None
        
        return {
            'worldState': worldState,
            'robotState': robotState,
            'rsInstances': rsInstances_dict,
            'nlconCallbacks': nlconCallbacks,
            'objectiveCallback': objectiveCallback,
            'waypoint': waypoint,
            'bounds': bounds,
            'num_parameters': num_parameters,
            'guess': guess,
            'trajectory': trajectory,
            'cost': cost,
            'parameters': parameters,
            'successes': successes,
            'solution_idx': min_idx,
        }
             

    class merge_constraints:
        '''
        A functor for computing the constraints
        for a given input, with lookup for speed
        optimizations
        '''
        def __init__(self, nlconCallbacks: dict[str, Callable], buffer_size=16):
            self.buffer: list[float, tuple] = list()
            self.buffer_size = buffer_size
            self.nlconCallbacks = nlconCallbacks
        
        
        def __call__(self, k):
            '''
            Overload call to work as a functor.
            Utility function to merge the constraints
            '''
            if ((res:=self.findBuffer(k)) != None):
                return res
            
            # calculate result
            h = list()
            heq = list()
            grad_h = list()
            grad_heq = list()
            
            for nlconCb in self.nlconCallbacks.values():
                (rs_h, rs_heq, rs_grad_h, rs_grad_heq) = nlconCb(k)
                h.append(rs_h)
                heq.append(rs_heq)
                grad_h.append(rs_grad_h)
                grad_heq.append(rs_grad_heq)
               
            res = (h, heq, grad_h, grad_heq)
            
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