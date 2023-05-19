if __name__ == '__main__':
    # add modules to path
    import sys
    from matplotlib.pyplot import xlim, ylim
    sys.path.append("../../")
    
    # import modules
    from demos.box2d import BoxAgent, BoxAgentInfo, BoxAgentVisual
    from rtd.entity.components import GenericEntityState
    from rtd.sim.systems.patch_visual import PatchVisualSystem
    
    
    
    # create BoxAgent
    info = BoxAgentInfo(width=2, color=[0.5, 0.2, 1])
    state = GenericEntityState(info, n_states=2)
    visual = BoxAgentVisual(info, state)
    agent = BoxAgent(info=info, state=state, visual=visual)
    
    # show that the objects in each components are all linked
    print(agent.info)
    print(agent.state)
    print(agent.visual)
    
    '''
    agent.state.commit_state_data(2, [1, 2])
    print(agent.state.get_state())
    agent.reset()
    print(agent.state.get_state())
    #print(agent.getoptions())'''
    
    # add states
    agent.state.commit_state_data(2, [ 0,-2])   # ( 0,-2) at t=2
    agent.state.commit_state_data(5, [-2, 1])   # (-2, 1) at t=7
    agent.state.commit_state_data(2, [-4,-1])   # (-4,-1) at t=9
    agent.state.commit_state_data(3, [ 4, 3])   # ( 4, 3) at t=12
    agent.state.commit_state_data(2, [ 2, 0])   # ( 2, 0) at t=14
    
    # set up visual system and animate
    vs = PatchVisualSystem(dynamic_objects=agent.visual)
    xlim((-5, 5))
    ylim((-5, 5))
    vs.updateVisual(10)