import numpy as np
from scipy.spatial.transform import Rotation
from rtd.util.mixins.Typings import Vecnp



def rescale(vec: Vecnp, scale_min: float, scale_max: float,
            input_min: float = None, input_max: float = None, modify: bool = False) -> Vecnp:
    '''
    clamps vec in the range [input_min, input_max], then rescales
    elements of vec to land in the range [scale_min, scale_max].
    Modifies the original vec if modify=True
    '''
    # avoid modifying original
    if not modify:
        vec = vec.copy()
    
    # clamp
    if input_min is not None:
        vec = np.maximum(vec, input_min)
    if input_max is not None:
        vec = np.minimum(vec, input_max)
    
    # rescale
    scale_range = scale_max - scale_min
    vec -= vec.min()                # vec = [0,vec.max()]
    vec *= (scale_range/vec.max())  # vec = [0, scale_max - scale_min]
    vec += scale_min                # vec = [scale_min, scale_max]
    
    return vec


def axang2rotm(axis: Vecnp, angle: float):
    r = Rotation.from_rotvec(angle * axis)
    return r.as_matrix()