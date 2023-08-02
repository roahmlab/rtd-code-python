from trimesh import Trimesh
from rtd.sim.systems.patch3d_collision import Patch3dDynamicObject, Patch3dObject
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmKinematics
from collections import OrderedDict
from nptyping import NDArray



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
    
    
    def getCollisionObject(self, q = None, time = None) -> Patch3dObject:
        '''
        '''
        if q is None:
            q = self.arm_state.position[:,-1]       # last position
        if time is not None:
            q = self.arm_state.get_state(time).q    # position at given time
        config = self.arm_state.get_state(time).q
        fk: OrderedDict[Trimesh, NDArray] = self.arm_info.robot.visual_trimesh_fk(cfg=config)
        meshes = [mesh.copy().apply_transform(transform) for mesh, transform in fk.items()]
        return [Patch3dObject(mesh, id(self.arm_info)) for mesh in meshes]
        # make patch3dcollision system handle multiple Patch3dObjects returned from getcollisionobject
        
         