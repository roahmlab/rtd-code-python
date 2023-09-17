if __name__ == '__main__':
    #-------------------- imports --------------------#
    print("Loading modules...")
    from armour import ArmourAgent, ArmourSimulation
    from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourAgentVisual, ArmourAgentCollision, ArmourIdealAgentDynamics, ArmourMexController
    from rtd.entity.box_obstacle import BoxObstacleInfo, BoxObstacleVisual, BoxObstacleCollision, BoxObstacle
    from rtd.entity.components import GenericEntityState
    from rtd.sim.systems.visual import PyvistaVisualSystem
    from rtd.sim.systems.collision import TrimeshCollisionSystem
    from urchin import URDF
    import numpy as np
    
    # configure logging
    from rtd.functional.logconfig import config_logger
    config_logger('INFO')
    
    
    
    #-------------------- agent parameters --------------------#
    agent_urdf = "../../urdfs/kinova_arm/kinova_without_gripper.urdf"
    add_uncertainty_to = 'all'  # choose 'all', 'link', 'none'
    links_with_uncertainty = ['dumbell_link']
    uncertain_mass_range = (0.97, 1.03)
    
    component_options = {
        "dynamics": {
            "measurement_noise_points": 0,
        },
        
        "controller": {
            "use_true_params_for_robust": True,
        },
        
        "visual": {
            "face_opacity": 1,
        },
    }
    
    
    
    #-------------------- setup the agent --------------------#
    robot = URDF.load("../../urdfs/kinova_arm/kinova_without_gripper.urdf")
    params = {
        "gravity": [0, 0, -9,81],
    }
    vel_limits = [[-1.3963, -1.3963, -1.3963, -1.3963, -1.2218, -1.2218, -1.2218],
                  [1.3963,  1.3963,  1.3963,  1.3963,  1.2218,  1.2218,  1.2218]]
    input_limits = [[-56.7, -56.7, -56.7, -56.7, -29.4, -29.4, -29.4],
                    [56.7,  56.7,  56.7,  56.7,  29.4,  29.4,  29.4]]
    transmision_inertia = [8.02999999999999936, 11.99620246153036440, 9.00254278617515169, 11.58064393167063599, 8.46650409179141228, 8.85370693737424297, 8.85873036646853151]
    M_min_eigenvalue = 5.095620491878957
    
    agent_info = ArmourAgentInfo(robot, params, joint_velocity_limits=vel_limits, joint_torque_limits=input_limits,
                                 transmission_inertia=transmision_inertia, M_min_eigenvalue=M_min_eigenvalue)
    
    armour_controller = ArmourMexController
    
    agent = ArmourAgent(info=agent_info, controller=armour_controller, component_options=component_options)
    
    
    
    #-------------------- create the simulation --------------------#
    sim = ArmourSimulation()
    sim.setup(agent)
    sim.initialize()
    sim.visual_system.waituntilclose()