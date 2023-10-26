Entities and Agents
===================

Entities define objects that exist in the simulated world with a variety of properties.
This simulator works on mixed Entity-Component (EC) and Entity-Component-System (ECS)
architecture. Each entity aggregates a few core components with special cases aggregating
any additional necessary components. Entity data purely exists in the components. Components
can be categorized as Data Components, Data + Behavior Components, and Behavior Components.

To see a demo for making your own basic entity, refer to the Box2D Agent example in the