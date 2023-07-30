from trimesh import Trimesh
from rtd.sim.systems.patch3d_collision import Patch3dDynamicObject, Patch3dObject
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmKinematics



class ArmourPatchCollision(Patch3dDynamicObject):
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState, kinematics: ArmKinematics):
        # initialize base classes
        Patch3dDynamicObject.__init__(self)
        # initialize
        self.arm_info = arm_info
        self.arm_state = arm_state
        self.kinematics = kinematics
        
        self.reset()
    
    
    def reset(self):
        self.create_collision_patch_data()
    
    
    def create_collision_patch_data(self):
        '''
        create list of meshes
        '''
        self.meshes: list[Trimesh] = [link.collision_mesh for link in self.arm_info.robot.links]
    
    
    def getCollisionObject(self, q = None, time = None) -> Patch3dObject:
        if q == None:
            q = self.arm_state.position[:,-1]       # last position
        if time != None:
            q = self.arm_state.get_state(time).q    # position at given time
        
         