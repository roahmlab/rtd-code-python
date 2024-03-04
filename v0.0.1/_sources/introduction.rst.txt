Introduction
============

This is the Python implementation of the original MATLAB RTD Architecture Code Base. It is a near
one to one implementation of the original code, with a few Python specific changes, as well as
changes to the architecture which will likely get backported into the MATLAB version in the near
future. Please note this version may be subject to significant changes in the future.

In here, the code is split up into many different packages, with a somewhat flattened out structure.
Changing out smaller behaviors of an agent or simulator involves looking at files that pertain to that
specific behavior instead of the whole simulator or agent.

Additionally, the code is written with the intention of making it more explicit. For example,
in the agent's `update` function, you now write out all components involved in the update of the
agent's internal behavior. In the simulator, you write out the update calls to entities and systems
manually, and can update multiple times per timestep.

Time should be tracked across everything to (1) make it easier to manage time, and (2) enable
validation functions to make sure all involved parts are updated accordingly.