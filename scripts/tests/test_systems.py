if __name__ == '__main__':
    print("Loading modules...")
    from armour import ArmourAgent
    from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourAgentVisual, ArmourAgentCollision
    from rtd.entity.box_obstacle import BoxObstacleInfo, BoxObstacleVisual, BoxObstacleCollision, BoxObstacle
    from rtd.entity.components import GenericEntityState
    from rtd.sim.systems.visual import PyvistaVisualSystem
    from rtd.sim.systems.collision import TrimeshCollisionSystem
    from urchin import URDF
    import os
    import numpy as np

    # configure logging
    from rtd.functional.logconfig import config_logger
    config_logger('INFO')


    # load robot
    print("Loading URDF...")
    urdf_path = os.path.join(os.path.dirname(__file__), "../../urdfs/kinova_arm/kinova_without_gripper.urdf")
    robot = URDF.load(urdf_path)

    # generate Armour Components 
    arm_info = ArmourAgentInfo(robot, None)
    arm_state = ArmourAgentState(arm_info)
    arm_visual = ArmourAgentVisual(arm_info, arm_state, edge_width=0)
    arm_collision = ArmourAgentCollision(arm_info, arm_state)
    arm_state.reset()
    print(f"Info:\n{arm_info}")
    print(f"State:\n{arm_state}")
    print(f"Visual:\n{arm_visual}")
    print(f"Collision:\n{arm_collision}")

    # generate armour agent
    arm_agent = ArmourAgent(arm_info, arm_state, arm_visual, arm_collision)
    print(f"Agent:\n{arm_agent}")


    # commit state at time=1
    time = np.array([0, 1])
    state = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1],
    ]).T
    arm_agent.state.commit_state_data(time, state)

    # commit more states at time=3, 4
    time = np.array([0, 2, 3])
    state = np.array([
        [1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1],
        [-1, -0.1, -1, 0.1, 1, 0.1, -1, 0.1, 1, 0.1, -1, 0.1, 1, 0.1],
        [-0.5, 0, -1, 0.1, 0.5, 0.1, -0.5, 0.1, -1, 0.1, -1, 0.1, -1, 0.1],
    ]).T
    arm_agent.state.commit_state_data(time, state)

    print(f"state.time: {arm_agent.state.time}")
    print(f"state.state:\n{arm_agent.state.state}")


    # add an obstacles
    box_info = BoxObstacleInfo(dims=[0.1,0.1,0.1], color=[1,0,0])
    box_state = GenericEntityState(box_info)
    box_state.reset(initial_state=[0,0,0.7])
    box_visual = BoxObstacleVisual(box_info, box_state, face_opacity=1)
    box_collision = BoxObstacleCollision(box_info, box_state)
    box_obstacle = BoxObstacle(box_info, box_state, box_visual, box_collision)



    # set up visual system
    vs = PyvistaVisualSystem(dynamic_objects=[arm_agent.visual, box_obstacle.visual], dimension=3)
    cs = TrimeshCollisionSystem(dynamic_objects=[arm_agent.collision, box_obstacle.collision])
    #vs.redraw(0)
    vs.updateVisual(3)
    vs.animate()
    vs.waituntilclose()

    cs.updateCollision(3)