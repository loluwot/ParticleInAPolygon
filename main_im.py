
import matplotlib.pyplot as plt
from matplotlib import cm
from image_to_poly import to_poly
from utils import *
import math
from matplotlib.animation import FuncAnimation

MODE = '3D'

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
polygon = Polygon(to_poly('trollface.png'))
polygon.normalize()
bbox_x, bbox_y = polygon.bbox()

ENERGIES = list(range(10))
hbar = 1

sol = boundary_approx(30, polygon)
xx = np.linspace(*bbox_x, 50)
yy = np.linspace(*bbox_y, 50)
X, Y = np.meshgrid(xx, yy)

thetas = [np.pi/4]*len(ENERGIES)
# cs = [np.cos(theta), np.sin(theta)]
cs = sphere_coord(thetas)

z_lim = sum([cs[i]**2*np.max(sol.n_sol(E)(X, Y)**2) for i, E in enumerate(ENERGIES)]) + sum([2*cs[i]*cs[j]*np.max(sol.n_sol(ENERGIES[i])(X, Y)*sol.n_sol(ENERGIES[j])(X, Y)) for i in range(len(ENERGIES)) for j in range(i)])
independent_part = sum([cs[i]**2*sol.n_sol(E)(X, Y)**2 for i, E in enumerate(ENERGIES)])
dependent_part = [[2*cs[i]*cs[j]*sol.n_sol(ENERGIES[i])(X, Y)*sol.n_sol(ENERGIES[j])(X, Y) for j in range(i)] for i in range(len(ENERGIES))]
def update(t):
    ax.clear()
    ax.set(xlim=bbox_x)
    ax.set(ylim=bbox_y)
    ax.set(zlim=(0, z_lim))
    polygon.draw()
    Z = independent_part + sum([dependent_part[i][j]*np.cos((ENERGIES[i] - ENERGIES[j])/hbar*t) for i in range(len(ENERGIES)) for j in range(i)])
    return ax.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.9,),
    
ani = FuncAnimation(fig, update, frames=np.linspace(0, 6.3, 300), blit=False, interval=2)
# ax.pcolormesh(X, Y, sol.n_sol(ENERGY)(X, Y)**2, cmap=cm.viridis)
# plt.show()
ani.save('test.gif', writer='Pillow', fps=30)