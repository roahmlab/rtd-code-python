from rtd.planner.trajectory import Trajectory, InvalidTrajectory
from rtd.entity.states import ArmRobotState
import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape['N'], Float64]



class BernsteinArmTrajectory(Trajectory):
    def __init__(self):
        # initialize base classes
        Trajectory().__init__(self)
        # set properties
        self.vectorized = True