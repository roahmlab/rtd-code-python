from rtd.util.mixins import Options
from rtd.planner import RtdPlanner
from rtd.entity.states import EntityState
from rtd.planner.trajectory import Trajectory
from rtd.planner.trajopt import TrajOptProps, RtdTrajOpt, GenericArmObjective, ScipyOptimizationEngine
from rtd.sim.world import WorldState
from armour.reachsets import JRSGenerator, FOGenerator, IRSGenerator, JLSGenerator
from armour.trajectory import ArmTrajectoryFactory
from zonopyrobots import ZonoArmRobot
from urchin import URDF



class ArmourPlanner(RtdPlanner, Options):
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "input_constraints_flag": False,
            "use_robust_input": False,
            "smooth_obs": False,
            "traj_type": "piecewise",
        }
        
        
    def __init__(self, trajOptProps: TrajOptProps, robot: URDF, params: ZonoArmRobot, **options):
        # initialize base classes
        RtdPlanner.__init__(self)
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.rsGenerators = dict()
        self.rsGenerators["jrs"] = JRSGenerator(params, traj_type=options["traj_type"])
        self.rsGenerators["fo"] = FOGenerator(params, self.rsGenerators["jrs"], smooth_obs=options["smooth_obs"])
        if options["input_constraints_flag"]:
            self.rsGenerators["irs"] = IRSGenerator(params, self.rsGenerators["jrs"], use_robost_input=options["use_robust_input"])
            self.rsGenerators["jls"] = JLSGenerator(params, self.rsGenerators["jrs"])
        
        # create the trajectory factory
        self.trajectoryFactory = ArmTrajectoryFactory(trajOptProps, options["traj_type"])
        
        # create the objective
        self.objective = GenericArmObjective(trajOptProps, self.trajectoryFactory)
        
        # selection of optimization engine
        self.optimizationEngine = ScipyOptimizationEngine(trajOptProps)
        
        # create the trajopt object
        self.trajopt = RtdTrajOpt(trajOptProps, self.rsGenerators, self.objective,
                                  self.optimizationEngine, self.trajectoryFactory)
    
    
    def planTrajectory(self, robotState: EntityState, worldState: WorldState, waypoint) -> tuple[Trajectory, dict]:
        '''
        Then on each waypoint, we call for a trajectory plan:
        Use RTD to solve for a trajectory and return either
        the parameters or invalid signal (continue).
        
        Loops over each RtdTrajOpt instance (thus, each trajectory
        type) with the given RobotState, WorldState, Waypoint, and
        initial guess. 
        
        From the results, selects the best valid Trajectory,
        otherwise return an invalid trajectory which will throw when
        attempting to set the new trajectory, ensuring the old one
        continues
        '''
        
        traj, _, info = self.trajopt.solveTrajOpt(robotState, worldState, waypoint)
        return traj, info