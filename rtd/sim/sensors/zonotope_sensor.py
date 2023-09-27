from rtd.sim.world import WorldEntity
from zonopy import zonotope



def zonotope_sensor(world: dict, agent: WorldEntity, time: float = None) -> list[zonotope]:
    # remove the agent, and mask only components with representations
    zonotopes_out = list()
    
    for id_entity, entity in world.items():
        if id_entity == id(agent):
            continue
        
        if hasattr(entity, "representation"):
            zonotopes_out.append(entity.representation.get_zonotope(time=time))
        
    return zonotopes_out