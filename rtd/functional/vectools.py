import numpy as np
from nptyping import NDArray, Shape, Float64

# type hinting
RowVec = NDArray[Shape["N"], Float64]



def rescale(vec: RowVec, scale_min: float, scale_max: float,
            input_min: float = None, input_max: float = None, modify: bool = False) -> RowVec:
    '''
    clamps vec in the range [input_min, input_max], then rescales
    elements of vec to land in the range [scale_min, scale_max].
    Modifies the original vec if modify=True
    '''
    # avoid modifying original
    if not modify:
        vec = vec.copy()
    
    # clamp
    if input_min != None:
        vec = np.maximum(vec, input_min)
    if input_max != None:
        vec = np.minimum(vec, input_max)
    
    # rescale
    scale_range = scale_max - scale_min
    vec -= vec.min()                # vec = [0,vec.max()]
    vec *= (scale_range/vec.max())  # vec = [0, scale_max - scale_min]
    vec += scale_min                # vec = [scale_min, scale_max]
    
    return vec