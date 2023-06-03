from rtd.sim.systems.patch_visual import mesh_to_artist
from trimesh import Trimesh as mesh
import numpy as np
import matplotlib.pyplot as plt
from rtd.sim.systems.patch3d_collision import Patch3dObject, Patch3dDynamicObject, Patch3dCollisionSystem

fig = plt.figure()
ax = fig.add_subplot(projection="3d")

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



class DynamicObject(Patch3dDynamicObject):
    def getCollisionObject(self, time):
        transform = np.array([0, 0, 2-time])
        msh = mesh(np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]) + transform, np.array([[0,1,2],[0,1,3],[0,2,3],[1,2,3]]))
        return Patch3dObject(msh)
    
    
    def __init__(self):
        Patch3dDynamicObject.__init__(self)


patch1 = DynamicObject()

obj1_artist = mesh_to_artist(patch1.getCollisionObject(2).mesh, edgecolor="black")
ax.add_artist(obj1_artist)

obj2 = mesh(np.array([[0,0,-1],[0,0,1],[0,0.5,1],[0.5,0,1]]), np.array([[0,1,2],[0,1,3],[0,2,3],[1,2,3]]))
obj2_artist = mesh_to_artist(obj2, edgecolor="red")
ax.add_artist(obj2_artist)


plt.show()

patch2 = Patch3dObject(obj2)
cs = Patch3dCollisionSystem(static_objects=patch2, dynamic_objects=patch1)


cs.updateCollision(5)