from rtd.planner.trajectory import Trajectory



class ArmourController:
    def __init__(self, *todo, **more_todo):
        self.k_r = None
        self.ultimate_bound = None
        self.trajectories: list[Trajectory] = None
    
    
    def reset(self, *todo, **more_todo):
        pass