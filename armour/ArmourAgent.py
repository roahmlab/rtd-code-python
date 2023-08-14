from rtd.sim.world import WorldEntity
from armour.agent import ArmourAgentDynamics, ArmourAgentInfo, ArmourAgentState, ArmourAgentVisual, ArmourAgentCollision



class ArmourAgent(WorldEntity):
    '''
    The Agent with the robust controller for ARMOUR
    '''
    @staticmethod
    def defaultoptions() -> dict:
        return {
            "components": {
                "info": ArmourAgentInfo,
                "state": ArmourAgentState,
                "visual": ArmourAgentVisual,
                "collision": ArmourAgentCollision,
            },
        }
    
    
    def __init__(self, info: ArmourAgentInfo = ArmourAgentInfo,
                 state: ArmourAgentState = ArmourAgentState,
                 visual: ArmourAgentVisual = ArmourAgentVisual, 
                 collision: ArmourAgentCollision = ArmourAgentCollision, **options):
        WorldEntity.__init__(self)
        components = {
            "info": info,
            "state": state,
            "visual": visual,
            "collision": collision,
        }
        # Get override options based on provided components
        override_options = self.get_componentOverrideOptions(components)
        
        # Merge all options
        self.mergeoptions(options, override_options)
        
        # (Re)construct all components for consistency
        self.info = info
        self.construct_components("state", self.info)
        self.construct_components("visual", self.info, self.state)
        self.construct_components("collision", self.info, self.state)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()
    
    
    def update(self, t_move):
        pass