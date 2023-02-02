
import matplotlib.pyplot as plt
from matplotlib import cm
from image_to_poly import to_poly
from utils import *
import math
from matplotlib.animation import FuncAnimation

MODE = '3D'

polygon = Polygon.ngon(1, 100, normalize=True)
# polygon = Polygon(to_poly('human.jpg', alpha=3))
# polygon = Polygon(to_poly('benzene.png'))
bbox_x, bbox_y = polygon.bbox()
import random
# ENERGIES = list(random.sample(range(10), 5))
ENERGIES = [0, 1]
hbar = 1

V = lambda x, y: -1/max(1e-6, math.sqrt(x**2+y**2))

sol = boundary_approx(60, polygon, potential_function=V)
# sol = boundary_approx(60, polygon)

# thetas = [np.random.uniform(0, math.pi/2) for _ in range(len(ENERGIES))]
thetas = [np.pi/4]*len(ENERGIES)
cs = sphere_coord(thetas)
print(sol.energy)
# print(sol2.energy)
def save_anim(sol, cs, ENERGIES, anim_name='test.gif', frames=100):
    z_lim = sum([cs[i]**2*np.max(sol.n_sol(E)(X, Y)**2) for i, E in enumerate(ENERGIES)]) + sum([2*cs[i]*cs[j]*np.max(np.abs(sol.n_sol(ENERGIES[i])(X, Y)*sol.n_sol(ENERGIES[j])(X, Y))) for i in range(len(ENERGIES)) for j in range(i)])
    independent_part = sum([cs[i]**2*sol.n_sol(E)(X, Y)**2 for i, E in enumerate(ENERGIES)])
    dependent_part = [[2*cs[i]*cs[j]*sol.n_sol(ENERGIES[i])(X, Y)*sol.n_sol(ENERGIES[j])(X, Y) for j in range(i)] for i in range(len(ENERGIES))]
    def update(t):
        ax.clear()
        ax.set(xlim=bbox_x)
        ax.set(ylim=bbox_y)
        ax.set(zlim=(0, z_lim))
        polygon.draw()
        Z = independent_part + sum([dependent_part[i][j]*np.cos((sol.energy[ENERGIES[i]] - sol.energy[ENERGIES[j]])/hbar*t) for i in range(len(ENERGIES)) for j in range(i)])
        return ax.plot_surface(X, Y, Z, cmap=cm.viridis, alpha=0.9,),
    ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*math.pi/(max(L := [sol.energy[x] for x in ENERGIES])- min(L)), frames), blit=False, interval=2)
    ani.save(anim_name, writer='Pillow', fps=30)

fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# cs = [math.sqrt(1/len(ENERGIES)) for _ in ENERGIES]
# save_anim(sol, cs, ENERGIES, anim_name='with_potential.gif')
# save_anim(sol2, cs, ENERGIES, anim_name='no_potential.gif')
# polygon.draw()
# ax.plot_surface(X, Y, sol.n_sol(0)(X, Y)**2, cmap=cm.viridis, alpha=0.9)
# # ax.plot_surface(X, Y, sol.n_sol(1)(X, Y)**2, cmap=cm.viridis, alpha=0.9)
xx = np.linspace(*bbox_x, 100)
yy = np.linspace(*bbox_y, 100)
X, Y = np.meshgrid(xx, yy)
ax = fig.add_subplot(111, projection='3d')
# ax.set_aspect('equal', adjustable='box')

# for i in range(10):
#     ax.plot_surface(X, Y, sol.n_sol(i)(X, Y), cmap=cm.viridis, alpha=0.9)
#     polygon.draw()
#     fig.savefig(f'circle/{i}.png') 
#     ax.clear()
# ax.pcolormesh(X, Y, abs(sol.n_sol(3)(X, Y))**2, cmap=cm.viridis)
ax.plot_surface(X, Y, sol.n_sol(5)(X, Y), cmap=cm.viridis, alpha=0.9)
polygon.draw()
plt.show()