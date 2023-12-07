"""from rtd.util.mixins import Options
from armour.agent import ArmourAgentInfo, ArmourAgentState
from rtd.functional.vectools import axang2rotm
import numpy as np
from collections import OrderedDict
from nptyping import NDArray

# define top level module logger
import logging
logger = logging.getLogger(__name__)



class ArmKinematics(Options):
    '''
    A collection of useful function for arm robot kinematics
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return dict()
    
    
    def __init__(self, arm_info: ArmourAgentInfo, arm_state: ArmourAgentState, **options):
        # initialize base classes
        Options.__init__(self)
        # initialize using given options
        self.mergeoptions(options)
        self.arm_info = arm_info
        self.arm_state = arm_state
        
        # self.reset
    
    
    def reset(self, **options):
        self.mergeoptions(options)
    
    
    def get_link_transform(self, time):
        if time > self.arm_state.time[-1]:
            time = self.arm_state.time[-1]
            logger.warn("Invalid time entered! Using agent''s final time t={t} instead.")
        # interpolate the state for the corresponding time
        config = self.arm_state.get_state(time).position
        return self.get_link_transform_from_config(config)
        
    
    
    def get_link_transform_from_config(self, config):
        fk: OrderedDict[Trimesh, NDArray] = self.arm_info.urdf.visual_trimesh_fk(cfg=config)
        return fk.values()[1:]
    
    
    def get_link_rotations_and_translations(self, time_or_config: float | NDArray = 0, cad_flag: bool = False) -> tuple[NDArray, NDArray, NDArray]:
        # get joint data
        if isinstance(t, float) or isinstance(t, int):
            t = time_or_config
            if t > self.arm_state.time[-1]:
                t = self.arm_state.time[-1]
                logger.warn("Invalid time entered! Using agent''s final time t={t} instead.")
            # interpolate the state for the corresponding time
            j_vals = self.arm_state.get_state(t).position
        
        # assume config was given
        else:
            q: NDArray = time_or_config
            if q.size == self.arm_state.n_states:
                q = q[self.arm_state.position_indices]
            elif q.size != self.arm_info.n_q:
                raise Exception("Please provide either a time or a joint configuration.")
            j_vals = q
        
        # extract dimensions
        dim = self.arm_info.dimension
        n_links = self.arm_info.n_links_and_joints
        
        # joint location
        j_locs = self.arm_info.joints.location
        if cad_flag:
            # We restore the original not-link-centered locations
            last_offset = j_locs[dim:, 0]
            j_locs[dim:, 0] = 0
            for i in range(n_links):
                j_locs[:dim, i] -= last_offset
                last_offset = j_locs[dim:, i]
                j_locs[dim:, i] = 0
        
        # allocate arrays for the rotations, translations, and join locations
        R = np.repeat([np.eye(dim)], n_links, axis=0)
        T = np.repeat([np.zeros(dim)], n_links, axis=0)
        J = np.nan((dim, n_links))
        
        # move through the kinematic chain and get the rotations and
        # translation of each link
        for idx in range(n_links):
            k_idx = self.arm_info.kinematic_chain[:,idx]
            p_idx = k_idx[0]
            s_idx = k_idx[1]
            
            # get the rotation and translation of the predecessor and
            # successor links we assume the baselink is always rotated
            # to an angle of 0 and with a translation of 0
            if p_idx == 0:
                R_pred = np.eye(dim)
                T_pred = np.zeros(dim)
            else:
                R_pred = R[p_idx]
                T_pred = T[p_idx]
            
            # get the location of the current joint
            j_loc = j_locs[:,idx]
            
            # compute link rotation
            match self.arm_info.joints[idx].type:
                case 'revolute':
                    # get value of current joint
                    joint_rot = j_vals[self.arm_info.body_joint_index[idx]]
                    if dim == 3:
                        # rotation matrix of current link
                        axis_pred = self.arm_info.joints[idx].axes
                        # TODO
                        R_succ = R_pred*self.arm_info.robot.Bodies[idx].Joint.JointToParentTransform[:3, :3]*axang2rotm(axis_pred, joint_rot)
                    else:
                        # rotation matrix of current link
                        rotation = np.array([[np.cos(joint_rot), -np.sin(joint_rot)],
                                            [np.sin(joint_rot), np.cos(joint_rot)]])
                        R_succ = rotation*R_pred
                    
                    # create translation
                    T_succ = T_pred + R_pred*j_loc[:dim] - R_succ*j_loc[dim:]
                    
                case 'prismatic':
                    raise NotImplementedError("Prismatic joints are not yet supported!")
                
                case 'fixed':
                    if dim == 3:
                        # TODO
                        R_succ = R_pred*self.arm_info.robot.Bodies[idx].Joint.JointToParentTransform[:3, :3]
                    else:
                        # rotation matrix of current link assumed same as predecessor
                        R_succ = R_pred

                    # create translation
                    T_succ = T_pred + R_pred*j_loc[:dim] - R_succ*j_loc[dim:]

                case _:
                    raise Exception("Invalid joint type!")
            
            # fill in rotation and translation cells
            R[s_idx] = R_succ
            T[s_idx] = T_succ
            
            # fill in the joint location
            j_loc_local = j_locs[dim:,idx]
            J[:,idx] = -R_succ*j_loc_local + T_succ
        return (R, T, J)
"""