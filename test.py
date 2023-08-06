print("Loading modules...")
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourAgentVisual
from rtd.sim.systems.patch_visual import PyvistaVisualSystem
from urchin import URDF
import numpy as np


# load robot
print("Loading URDF...")
robot = URDF.load("./urdfs/kinova_arm/kinova_without_gripper.urdf")


# generate info 
print("Generating Info Component: ")
arm_info = ArmourAgentInfo(robot, None)
print(arm_info)


# generate state
print("Generating State Component: ")
arm_state = ArmourAgentState(arm_info)
arm_state.reset()
print(arm_state)


# generate visual
print("Generating Visual Component: ")
arm_visual = ArmourAgentVisual(arm_info, arm_state)
print(arm_visual)


# commit state at time=1
time = np.array([0, 1])
state = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1],
]).T
arm_state.commit_state_data(time, state)

# commit more states at time=3, 4
time = np.array([0, 2, 3])
state = np.array([
    [1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1],
    [-1, -0.1, -1, 0.1, 1, 0.1, -1, 0.1, 1, 0.1, -1, 0.1, 1, 0.1],
    [-0.5, 0, -1, 0.1, 0.5, 0.1, -0.5, 0.1, -1, 0.1, -1, 0.1, -1, 0.1],
]).T
arm_state.commit_state_data(time, state)

print(f"{arm_state.time=}")
print(f"{arm_state.state=}")


# set up visual system
vs = PyvistaVisualSystem(dynamic_objects=arm_visual, dimension=3)
vs.redraw(0)
vs.updateVisual(3)
vs.animate()
vs.waituntilclose()