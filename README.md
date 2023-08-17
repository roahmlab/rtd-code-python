# rtd-code-python
The original MATLAB RTD Planner and ARMOUR ported into Python



## Getting Started
*rtd-code-python requires Python 3 or higher. For best results, use Python 3.11.3*

1. Clone the repository and open a terminal in the root directory
2. Install *virtualenv* with `py -m pip install virtualenv`
3. Create a new Virtual Environment with `py -m venv rtd_venv`
4. Activate the Virtual Environment with `rtd_venv\scripts\activate`
5. Install *rtd-code-python* and its dependencies with `py -m pip install -r requirements.txt`
6. Optionally, open a terminal inside `scripts\demos` and run the demo scripts



## Key Features
- ARMOUR (`armour`)
- RTD Planner (`rtd/planner`)
- Agents and Components (`rtd/entity`)
- Visualization System using PyVista (`rtd/sim/systems/visual`)
- Collision System using Trimesh (`rtd/sim/systems/collision`)
- Agent and Visualization Demo (`scripts/demos/box2d_agent.py`)
- Armour Agent, Visualization, and Collision Demo (`scripts/tests/test_systems.py`)



## Changes from the original MATLAB code
### rtd/sim
- The collision and visualization systems do not have a pause function
- The collision and visualization systems have been renamed appropriately
- Added `get_discretization_and_pause()` to the visual system to help animate at a set FPS and speed
- Added `waituntilclose()` to the visual system (does exactly what you think it does)
- Visual system's `updateVisual()` no longer renders if `redraw()` hasn't been called before
- Visual system's `redraw()` and `animate()` takes a new `axlim` optional argument to specify the x,y, and z bounds
- The collision system uses mesh collisions rather than patches
- `WorldEntity`'s `get_componentOverrideOptions()` can take in either a class instance or the class itself (rather than a string of the name of the class)

### rtd/planner
- The solver inside the planner is implemented with `scripy.solve` as `fmincon` does not exist in Python
- `RtdTrajOpt`'s `merge_constraint()` is now a functor which uses caches
  
### rtd/util
- Removed `UUID` as they can be replaced by the `id()` function
- Removed `NamedClass` as the logging is handled by Python's `logging` module
  
### armour
- Removed `R_t` and `R_t_des` from `JRSInstance` as numpy and tensorflow already has a transpose function
- Trajectories no longer stores an internal `JRSInstance`. The factory instead pulls values from the instance when creating trajectories
- `ArmourAgentInfo` takes in a `urchin.URDF` object as the `robot` argument



## Not Implemented Yet
- [ ] armour/agent/ArmourMexController
- [ ] armour/agent/ArmourDynamics
- [ ] armour/ArmourSimulation
- [ ] armour/reachsets/IRSGenerator



## Tested Features
- [x] rtd/demos
- [x] rtd/entity
- [x] rtd/functional
- [ ] rtd/planner
- [x] rtd/sim/systems/visual
- [x] rtd/sim/systems/collision
- [x] rtd/sim/world
- [x] rtd/util
- [x] armour/agent
- [ ] armour/legacy
- [ ] armour/reachsets
- [ ] armour/trajectory
- [x] armour/ArmourAgent
- [ ] armour/ArmourPlanner