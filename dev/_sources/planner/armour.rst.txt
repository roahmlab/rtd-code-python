Example RTD Planner Implementation of ARMOUR
============================================

ArmourPlanner and these related components define the ARMOUR planner as described by Michaux et. al. in https://arxiv.org/abs/2301.13308.
This planner requires the use of the matching robust controller.
Currently a kinematics-only minimal version of this is implemented.

The Base ARMOUR Planner
-----------------------
.. autoclass:: armour.ArmourPlanner.ArmourPlanner
   :show-inheritance:
   :members:
   :undoc-members:

Reachable Set Generation
------------------------
.. automodule:: armour.reachsets
   :show-inheritance:
   :members:
   :undoc-members:
.. currentmodule:: armour.reachsets

Generation of reachable sets are implemented as constraint generating classes, with the following classes generating instances for the constraints.

.. autosummary::
    :toctree: generated
    :nosignatures:

    JRSGenerator
    JLSGenerator
    FOGenerator
    IRSGenerator

.. autosummary::
    :toctree: generated
    :nosignatures:

    JRSInstance
    JLSInstance
    FOInstance
    IRSInstance

Trajectory Types and Factory
----------------------------
.. automodule:: armour.trajectory
   :show-inheritance:
   :members:
   :undoc-members:
.. currentmodule:: armour.trajectory

.. autosummary::
    :toctree: generated
    :nosignatures:

    ZeroHoldArmTrajectory
    PiecewiseArmTrajectory
    BernsteinArmTrajectory
    ArmTrajectoryFactory
