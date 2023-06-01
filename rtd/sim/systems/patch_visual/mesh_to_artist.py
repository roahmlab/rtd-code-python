from trimesh import Trimesh
from mpl_toolkits.mplot3d import art3d



def mesh_to_artist(mesh: Trimesh):
    '''
    Takes in a trimesh.Trimesh object and creates
    a matplotlib.artist object to use in the visual
    system
    '''
    v = mesh.vertices
    f = mesh.faces
    
    return art3d.Poly3DCollection(v[f])