if __name__ == '__main__':
    #-------------------- imports --------------------#
    print("Loading modules...")
    from armour import ArmourAgent, ArmourSimulation, ArmourPlanner
    from armour.agent import ArmourAgentInfo, ArmourController
    from armour.legacy import StraightLineHLP
    from rtd.planner.trajopt import TrajOptProps
    from rtd.sim.world import WorldState
    from zonopy.robots2.robot import ZonoArmRobot
    from urchin import URDF
    import os
    
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
            "edge_width": 0,
        },
    }
    
    
    
    #-------------------- setup the agent --------------------#
    urdf_path = os.path.join(os.path.dirname(__file__), agent_urdf)
    robot = URDF.load(urdf_path)
    params = ZonoArmRobot.load(robot)

    vel_limits = [[-1.3963, -1.3963, -1.3963, -1.3963, -1.2218, -1.2218, -1.2218],
                  [1.3963,  1.3963,  1.3963,  1.3963,  1.2218,  1.2218,  1.2218]]
    input_limits = [[-56.7, -56.7, -56.7, -56.7, -29.4, -29.4, -29.4],
                    [56.7,  56.7,  56.7,  56.7,  29.4,  29.4,  29.4]]
    transmision_inertia = [8.02999999999999936, 11.99620246153036440, 9.00254278617515169, 11.58064393167063599, 8.46650409179141228, 8.85370693737424297, 8.85873036646853151]
    M_min_eigenvalue = 5.095620491878957
    
    agent_info = ArmourAgentInfo(robot, params, joint_velocity_limits=vel_limits, joint_torque_limits=input_limits,
                                 transmission_inertia=transmision_inertia, M_min_eigenvalue=M_min_eigenvalue)
    
    armour_controller = ArmourController
    
    agent = ArmourAgent(info=agent_info, controller=armour_controller, component_options=component_options)
    
    
    
    #-------------------- create the simulation --------------------#
    sim = ArmourSimulation()
    sim.setup(agent)
    sim.initialize()
    #sim.visual_system.waituntilclose()
    
    
    
    #-------------------- interface of the planner --------------------#
    trajOptProp = TrajOptProps(
        timeForCost=1,
        planTime=0.5,
        horizonTime=1,
        doTimeout=False,
        timeoutTime=0.5,
        randomInit=True
    )
    
    input_constraints_flag = False
    use_robust_input = False
    smooth_obs = False
    
    planner = ArmourPlanner(
        trajOptProps=trajOptProp,
        robot=sim.agent,
        params=params,
        input_constraints_flag=input_constraints_flag,
        use_robust_input=use_robust_input,
        smooth_obs=smooth_obs,
        traj_type="bernstein"
    )
    #-------------------- high level planner --------------------#
    world_info = {'goal': sim.goal_system.goal_position}
    HLP = StraightLineHLP()
    HLP.setup(world_info)
    
    
    
    #-------------------- run planning step by step --------------------#
    def planner_callback(sim: ArmourSimulation, planner: ArmourPlanner, agent_info: ArmourAgentInfo,
                         world_info: dict, lookahead: float, HLP) -> dict:
        # get the end state
        time = sim.agent.state.time[-1]
        ref_state = sim.agent.controller.trajectories[-1].getCommand(time)
        agent_info.state = sim.agent.state.state[:, -1]
        
        q_des = HLP.get_waypoint(sim.agent.state.state[:,-1], lookahead)
        if q_des is None:
            print("Waypoint creation failed! Using global goal instead.")
            q_des = HLP.goal
        
        worldState = WorldState()
        #worldState.obstacles = zonotope_sensor(sim.world, sim.agent, time)
        trajectory, plan_info = planner.planTrajectory(ref_state, worldState, q_des)
        
        if trajectory is not None:
            sim.agent.controller.setTrajectory(trajectory)
        
        return plan_info
    
    
    lookahead = 0.4
    cb = lambda s: planner_callback(s, planner, agent_info, world_info, lookahead, HLP)
    sim.run(max_steps=100, pre_step_callback=cb)