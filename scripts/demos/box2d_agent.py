if __name__ == '__main__':
    # add modules to path
    import os
    import sys
    from matplotlib.pyplot import xlim, ylim
    sys.path.append("../../")
    
    # import modules
    from demos.box2d import BoxAgent, BoxAgentInfo, BoxAgentVisual
    from rtd.entity.components import GenericEntityState
    from rtd.sim.systems.patch_visual import PatchVisualSystem
    
    # configure logging
    import logging.config
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default_handler': {
                'class': 'logging.StreamHandler',
                'level': 'WARN',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default_handler'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)
    
    
    
    # create BoxAgent
    info1 = BoxAgentInfo(height=2, color=[0.5, 0.2, 1])
    state1 = GenericEntityState(info1, n_states=2)
    visual1 = BoxAgentVisual(info1, state1, edge_color=[1, 0, 0], edge_width=3, face_opacity=0.5)
    agent1 = BoxAgent(info=info1, state=state1, visual=visual1)
    
    info2 = BoxAgentInfo(width=2, height=0.5, color=[0, 1, 0])
    agent2 = BoxAgent(info=info2)
    
    # show that the objects in each components are all linked
    print(agent1.info)
    print(agent1.state)
    print(agent1.visual)
    
    # add states
    agent1.state.commit_state_data(1, [ 0,-2])   # ( 0,-2) at t=1
    agent1.state.commit_state_data(2, [-2, 1])   # (-2, 1) at t=3
    agent1.state.commit_state_data(1, [-4,-1])   # (-4,-1) at t=4
    agent1.state.commit_state_data(3, [ 4, 3])   # ( 4, 3) at t=7
    agent1.state.commit_state_data(2, [ 2, 0])   # ( 2, 0) at t=9
    
    # set up visual system
    vs = PatchVisualSystem(
        static_objects=agent2.visual,
        dynamic_objects=[agent1.visual],    # can take both single object or list of objects
        dimension=2,
    )
    time_discretization, pause_time = vs.get_discretization_and_pause(framerate=24, speed=1)
    
    # update time
    #vs.redraw(xlim=(-5, 5), ylim=(-5, 5))   # run this to render while update is running
    vs.updateVisual(9)
    
    # animate object
    vs.animate(
        time_discretization=time_discretization,
        pause_time=pause_time,
        xlim=(-5, 5),
        ylim=(-5, 5)
    )
    
    # wait until key pressed so program doesn't immediately close
    os.system('pause')