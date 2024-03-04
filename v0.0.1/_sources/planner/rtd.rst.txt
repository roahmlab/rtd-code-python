RTD Planner Interfaces and Base Classes
=======================================

The core components to any mid-level RTD Planner.

The RTD Planner
---------------

This is an interface to specify the midlevel planner.
It's written to be relatively isolated from the rest of the simulation package.

.. autoclass:: rtd.planner.RtdPlanner
   :show-inheritance:
   :members:
   :undoc-members:

Reachable Sets Generation Interfaces
------------------------------------
.. automodule:: rtd.planner.reachsets
   :show-inheritance:
   :members:
   :undoc-members:
.. currentmodule:: rtd.planner.reachsets

.. autosummary::
    :toctree: generated
    :nosignatures:

    ReachSetGenerator
    ReachSetInstance

Trajectory Interfaces
---------------------
.. automodule:: rtd.planner.trajectory
   :show-inheritance:
   :members:
   :undoc-members:
.. currentmodule:: rtd.planner.trajectory

.. autosummary::
    :toctree: generated
    :nosignatures:

    Trajectory
    InvalidTrajectory
    TrajectoryFactory
    TrajectoryContainer
    BadTrajectoryException

Trajectory Optimization Interfaces & Components
-----------------------------------------------
.. automodule:: rtd.planner.trajopt
   :show-inheritance:
   :members:
   :undoc-members:
.. currentmodule:: rtd.planner.trajopt

.. autosummary::
    :toctree: generated
    :nosignatures:

    TrajOptProps
    Objective
    GenericArmObjective
    OptimizationEngine
    ScipyOptimizationEngine
    RtdTrajOpt
