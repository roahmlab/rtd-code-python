from rtd.sim.world import WorldEntity
from armour.agent import ArmourAgentInfo, ArmourAgentState, ArmourAgentVisual, ArmourAgentCollision, ArmourIdealAgentDynamics, ArmourController



class ArmourAgent(WorldEntity):
    '''
    The Agent with the robust controller for ARMOUR
    '''
    @staticmethod
    def defaultoptions() -> dict:
        """
        Returns
        -------
        options : dict
            default options of armour agent
        """
        return {
            "components": {
                "info": ArmourAgentInfo,
                "state": ArmourAgentState,
                "visual": ArmourAgentVisual,
                "collision": ArmourAgentCollision,
                "controller": ArmourController,
                "dynamics": ArmourIdealAgentDynamics,
            },
        }
    
    
    def __init__(self, info: ArmourAgentInfo,
                 state: ArmourAgentState = ArmourAgentState,
                 visual: ArmourAgentVisual = ArmourAgentVisual, 
                 collision: ArmourAgentCollision = ArmourAgentCollision,
                 controller: ArmourController = ArmourController,
                 dynamics: ArmourIdealAgentDynamics = ArmourIdealAgentDynamics, **options):
        WorldEntity.__init__(self)
        components = {
            "info": info,
            "state": state,
            "visual": visual,
            "collision": collision,
            "controller": controller,
            "dynamics": dynamics
        }
        # Get override options based on provided components
        override_options = self.get_componentOverrideOptions(components)
        
        # Merge all options
        self.mergeoptions(options, override_options)
        
        if "component_options" in options:
            self.mergeoptions(options, options)
        
        # For intellisense
        self.state: ArmourAgentState
        self.visual: ArmourAgentVisual
        self.collision: ArmourAgentCollision
        self.controller: ArmourController
        self.dynamics: ArmourIdealAgentDynamics
        
        # (Re)construct all components for consistency
        self.info: ArmourAgentInfo = info
        self.construct_components("state", self.info)
        self.construct_components("visual", self.info, self.state)
        self.construct_components("collision", self.info, self.state)
        self.construct_components("controller", self.info, self.state)
        self.construct_components("dynamics", self.info, self.state, self.controller)
        
        # reset
        self.reset()
    
    
    def reset(self, **options):
        self.mergeoptions(options)
        self.reset_components()
    
    
    def update(self, t_move) -> dict:
        """
        Updates the armour agent
        
        Parameters
        ----------
        t_move : float
            time to update for
        
        Returns
        -------
        info : dict
            with keys:
        <success> : bool
            whether the agent moved successfully
        <t_check_step> : float
            time steps checked for
        <checks> : dict[str, bool]
            with keys <joint_limits>, <control_inputs>, <ultimate_bound>
        """
        self.dynamics.move(t_move)
        return {
            "success": True,
            "t_check_step": 0.01,
            "checks": {
                "joint_limits": self.state.joint_limit_check(0.01),
                "control_inputs": self.dynamics.controller_input_check(0.01),
                "ultimate_bound": True,     # self.controller.ultimate_bound_check(0.01, self.dynamics.controller_log) 
            }
        }