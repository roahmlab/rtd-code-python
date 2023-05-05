if __name__ == '__main__':
    # add modules to path
    import sys
    sys.path.append("../../")
    
    # import modules
    from demos.box2d import BoxAgent, BoxAgentInfo
    from rtd.entity.components import GenericEntityState
    
    
    
    # create BoxAgent
    info = BoxAgentInfo(width=2, color=[0.5, 0.2, 1])
    state = GenericEntityState(info, n_states=2)
    #state.random_init((-5, 5), save_to_options=True)
    agent = BoxAgent(info=info, state=state)
    
    
    print(agent.info)
    print(agent.state)
    agent.state.commit_state_data(2, [1, 2])
    print(agent.state.get_state())
    agent.reset()
    print(agent.state.get_state())
    #print(agent.getoptions())