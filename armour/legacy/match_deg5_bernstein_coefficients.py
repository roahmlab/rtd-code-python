from rtd.util.mixins.Typings import Vec



def match_deg5_bernstein_coefficients(traj_constraints: Vec, T: float = 1) -> Vec:
    '''
    match coefficients to initial position, velocity, acceleration (t=0)
    and final position, velocity, and acceleration (t=1)
    assuming a 5th degree bernstein polynomial (minimum degree necessary
    to satisfy these constraints)
    also assuming t in [0, T]
    '''
    q0 = traj_constraints[0]
    qd0 = traj_constraints[1]
    qdd0 = traj_constraints[2]
    q1 = traj_constraints[3]
    qd1 = traj_constraints[4]
    qdd1 = traj_constraints[5]
    
    beta = [
        q0,
        q0 + (T*qd0)/5,
        q0 + (qdd0*T*T)/20 + (2*qd0*T)/5,
        q1 + (qdd1*T*T)/20 - (2*qd1*T)/5,
        q1 - (T*qd1)/5,
        q1
    ]
    return beta