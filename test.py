from rtd.entity.components import GenericEntityState, EmptyInfoComponent

info = EmptyInfoComponent()
state = GenericEntityState(info, n_states=3, initial_state=[0, 0, 0])
#state.random_init((-10, 10), True)

print(state.get_state())

state.commit_state_data(2, [1, 3, 5])

print(state.get_state(1.6))
print(state.get_state())

state.commit_state_data(6, [4, 2, 6])

print(state.get_state(5))
print(state.get_state())

state.reset()
print(state.get_state())