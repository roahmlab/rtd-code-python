Components for Entities and Agents
==================================

Components can be categorized as Data Components, Data + Behavior Components, and Behavior
Components. Components should have specific purposes such as holding intrinsic data, or
defining entity dynamics. All behavior components transform entity data for use by either
another component or system and may or may not update entity data at the same time.

Entity-component modeled components are behavior or data-behavior components which should be
explicitly called by the entity update functions. Entity-component-system modeled components
are behavior or data-behavior components which are used by a system which should be explicitly
updated at any point of the simulation loop.

Base Components
---------------
.. automodule:: rtd.entity.components
   :imported-members:
   :show-inheritance:
   :members:
   :undoc-members:

Box Obstacle Components
-----------------------
.. autoclass:: rtd.entity.box_obstacle.BoxObstacleInfo
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: rtd.entity.box_obstacle.BoxObstacleVisual
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: rtd.entity.box_obstacle.BoxObstacleCollision
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: rtd.entity.box_obstacle.BoxObstacleZonotope
   :show-inheritance:
   :members:
   :undoc-members:

Armour Components
-----------------
.. automodule:: armour.agent
   :imported-members:
   :show-inheritance:
   :members:
   :undoc-members: