from rtd.entity.states import EntityState
from rtd.planner.reachsets import ReachSetInstance
from rtd.planner.trajectory import TrajectoryFactory, InvalidTrajectory
from rtd.planner.trajopt import TrajOptProps
from armour.reachsets import JRSInstance
from armour.trajectory import PiecewiseArmTrajectory, ZeroHoldArmTrajectory, BernsteinArmTrajectory
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class ArmTrajectoryFactory(TrajectoryFactory):
    def __init__(self, trajOptProps: TrajOptProps, traj_type: str = "piecewise"):
        # initialize base classes
        TrajectoryFactory.__init__(self)
        # set properties
        self.trajOptProps = trajOptProps
        self.traj_type = traj_type
    
    
    def createTrajectory(self, robotState: EntityState, rsInstances: dict[str, ReachSetInstance] = None,
                         trajectoryParams: RowVec = None, jrsInstance: JRSInstance = None,
                         traj_type: str = None) -> ZeroHoldArmTrajectory | PiecewiseArmTrajectory | BernsteinArmTrajectory:
        '''
        Create a new trajectory object for the given state
        '''
        if traj_type == None:
            traj_type = self.traj_type
        
        if traj_type != "zerohold" and jrsInstance == None:
            try:
                jrsInstance = rsInstances["jrs"]
            except:
                raise InvalidTrajectory("Must provide handle for JRSInstance if not generating a ZeroHoldArmTrajectory!")
        
        match traj_type:
            case "zerohold":
                trajectory = ZeroHoldArmTrajectory(self.trajOptProps, robotState)
            
            case "piecewise":
                trajectory = PiecewiseArmTrajectory(self.trajOptProps, robotState, jrsInstance)
            
            case "bernstein":
                trajectory = BernsteinArmTrajectory(self.trajOptProps, robotState, jrsInstance)
            
            case _:
                raise InvalidTrajectory("Traj_type must be one of 'zerohold', 'piecewise' or 'bernstein'!")
        
        if trajectoryParams != None:
            trajectory.setParameters(trajectoryParams)
        return trajectory