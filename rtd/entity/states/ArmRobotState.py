from rtd.entity.states import EntityState
from nptyping import NDArray



class ArmRobotState(EntityState):
    '''
    Information on the atomic state of the robot at a given point of
    time
    '''
    def __init__(self, position_indices: list[int] = None,
                 velocity_indices: list[int] = None, acceleration_indices: list[int] = None):
        # initialize base classes
        EntityState.__init__(self)
        # handle empty data
        if position_indices is None:
            position_indices = list()
        if velocity_indices is None:
            velocity_indices = list()
        if acceleration_indices is None:
            acceleration_indices = list()
        # set properties
        self.position_indices: list[int] = position_indices
        self.velocity_indices: list[int] = velocity_indices
        self.acceleration_indices: list[int] = acceleration_indices
        self.state: NDArray = None
    
    
    @property
    def position(self):
        return self.state[self.position_indices,:]
    
    @property
    def velocity(self):
        return self.state[self.velocity_indices,:]
    
    @property
    def acceleration(self):
        return self.state[self.acceleration_indices,:]
    
    # compat
    @property
    def q(self):
        return self.position
    
    @property
    def q_dot(self):
        return self.velocity
    
    @property
    def q_ddot(self):
        return self.acceleration
    
    @property
    def q_des(self):
        return self.position
    
    @property
    def q_dot_des(self):
        return self.velocity
    
    @property
    def q_ddot_des(self):
        return self.acceleration