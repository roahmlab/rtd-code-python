from zonopy.joint_reachable_set.gen_jrs import gen_traj_JRS
import numpy as np



def create_jrs_online(q, dq, ddq, joint_axes, taylor_degree, traj_type, add_ultimate_bound, LLC_info):
    if traj_type == "bernstein":
        raise NotImplementedError
    
    (q_des, dq_des, ddq_des, Q, dQ, dQ_a,
     ddQ_a, R_des, R_t_des, R, R_t) = gen_traj_JRS(q, dq, joint_axes, taylor_degree)
    
    n_q = q.size
    n_k = n_q
    c_k_orig = np.zeros(n_k)
    g_k_orig = np.min(np.max(np.pi/24, np.abs(dq/3)), np.pi/3)
    bernstein_center = np.zeros(n_q)
    berstein_final_range = np.pi/36 * np.ones(n_q)

    jrs_info = {
        'id': None,
        'id_names': None,
        'k_id': np.arange(n_q).reshape(n_q,1),
        'n_t': 1/0.01,
        'n_q': n_q,
        'n_k': n_k,
        'c_k_orig': c_k_orig,
        'g_k_orig': g_k_orig,
        'c_k_bernstein': bernstein_center,
        'g_k_bernstein': berstein_final_range,
    }
    return (q_des, dq_des, ddq_des, Q, dQ, dQ_a, ddQ_a, R_des, R_t_des, R, R_t, jrs_info)