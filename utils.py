import math
import networkx as nx
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
import itertools
pi = math.pi

def lsinc(N, k):
    h = 2/N
    def ff(*coords):
        res = np.ones(coords[0].shape)
        for i, kk in enumerate(k):
            chi_pos = (coords[i] + h*kk)*pi/(2*N*h)
            chi_neg = (coords[i] - h*kk)*pi/(2*N*h)
            temp = np.sin(chi_neg)
            temp[chi_neg == 0] = 1
            temp2 = np.cos(chi_pos)
            temp2[chi_pos == 0] = 1
            res *= (np.sin(((2*N + 1)*chi_neg))/temp) - (np.cos((2*N + 1)*chi_pos)/np.cos(chi_pos))
            res /= 2*N
        return res
    return ff

def lsinc_approx(N, zz):
    def approx(*coords):
        N = zz.shape[0] + 1
        res = np.zeros(coords[0].shape)
        for tup in itertools.product(range(N-1), repeat=len(coords)):
            res += zz[tup[::-1]]*lsinc(N, [i - N//2 + 1 for i in tup])(*coords)
        return res
    return approx

def boundary_approx(N, polygon):
    m_og = [(x, y) for x in range(-N//2 + 1, N//2) for y in range(-N//2 + 1, N//2) if polygon.in_poly((x*2/N, y*2/N))]
    def c2(k, j):
        if k == j:
            return -pi**2/24*(1 + 2*N**2 - 3/(math.cos(j*pi/N)**2))
        else:
            return (-1)**(j - k + 1)*pi**2/8*math.cos(j*pi/N)*math.cos(k*pi/N)/(math.cos((j+k)/2*pi/N)**2*math.sin((j-k)/2*pi/N)**2)
    h = np.zeros((len(m_og), len(m_og)))
    for i in range(len(m_og)):
        for j in range(len(m_og)):
            k, kp = m_og[i]
            l, lp = m_og[j]
            h[i][j] = -((c2(k, l) if kp == lp else 0) + (c2(kp, lp) if k == l else 0))
    sol_eig, sol_vec = np.linalg.eig(h)
    sols = [sol_vec[:,i] for i in sorted(range(len(sol_eig)), key=lambda i: sol_eig[i])]
    sol_energy = sorted(sol_eig)
    return Solution(sol_energy, sols, m_og, N)

class Polygon:
    def __init__(self, points): #assume adjacent points are connected
        self.points = points
        self.normalize()

    def normalize(self):
        x, y = zip(*self.points)
        x, y = sorted(x), sorted(y)
        avg = np.array([sum(x)/len(self.points), sum(y)/len(self.points)])
        self.points = np.array([(np.array(p) - avg) for p in self.points])
        self.points /= np.max([np.abs(np.min(self.points, axis=0)), np.max(self.points, axis=0)])
        
    def bbox(self):
        return (np.min(self.points[:, 0]), np.max(self.points[:, 0])), (np.min(self.points[:, 1]), np.max(self.points[:, 1]))

    def in_poly(self, point):
        points = self.points
        px, py = point
        crossings = 0
        for i in range(-1, len(points) - 1):
            ptop, pbot = sorted([points[i], points[i+1]], key = lambda x: -x[1])
            if py <= ptop[1] and py > pbot[1]:
                if px <= (py - pbot[1])/(ptop[1] - pbot[1])*(ptop[0] - pbot[0]) + pbot[0]:
                    crossings += 1
        return crossings % 2 == 1
    
    def draw(self):
        plt.plot(*zip(*(np.concatenate([self.points, np.array([self.points[0]])]))), 'k-')

class Solution:
    def __init__(self, energy, vecs, valid_grid, N):
        self.energy = energy
        self.N = N
        self.valid_grid = valid_grid
        self.vecs = vecs

    def n_sol(self, I):
        N = self.N
        zz = np.zeros((N-1, N-1))
        for i, v in enumerate(self.vecs[I]):
            x1, y1 = self.valid_grid[i]
            zz[y1 + N//2 - 1][x1 + N//2 - 1] = v
        return lsinc_approx(N, zz)

def distance(p1, p2):
    return math.sqrt(sum([(p1[i] - p2[i])**2 for i in range(len(p1))]))

def get_point(pos, points, dist=1):
    for circ, point in points.items():
        if distance(pos, point) < dist:
            return circ
    return None

def get_points_in_rect(rect, points):
    ordered_x = sorted([rect[i][0] for i in range(2)])
    ordered_y = sorted([rect[i][1] for i in range(2)])
    return list(filter(lambda point: ordered_x[0] <= point[1][0] <= ordered_x[1] and ordered_y[0] <= point[1][1] <= ordered_y[1], points.items()))

def to_graph(adj_list):
    G = nx.Graph()
    for point, neighbours in adj_list.items():
        G.add_node(point)
        for neighbour in neighbours:
            G.add_edge(point, neighbour)
    return G

def parse_polygon(adj_list):
    G = to_graph(adj_list)
    cycle = sorted(list(nx.simple_cycles(G.to_directed())), key=lambda x: len(x))[-1]
    return nx.cycle_graph(cycle)

def sign(x):
    return 0 if x == 0 else int(abs(x)//x)

def centroid(points):
    nppoints = list(map(np.array, points))
    return sum(nppoints)/len(nppoints)

def validate_polygon(polygon):
    positions, adj_list = polygon
    center = centroid(positions.values())
    def ang(points):
        vs = [[points[x][i] - points[1][i] for i in range(2)] for x in [2, 0]]
        return ((math.atan2(vs[0][1], vs[0][0]) - math.atan2(vs[1][1], vs[1][0])) + 2*math.pi) % (2*math.pi) - math.pi
    G = to_graph(adj_list)
    cycles = sorted(list(nx.simple_cycles(G.to_directed())), key=lambda x: len(x))
    if len(cycles) == 0:
        return False, None, None
    largest = cycles[-1]

    return nx.cycle_graph(largest).nodes()

    # print(largest)
    # #canonicalize to make cycles go in counterclockwise(?) order
    # rev = sign(ang([positions[largest[0]], center, positions[largest[-1]]]))
    # largest = largest[::rev]
    # circular_largest = list(map(lambda x: positions[x], largest*2))
    # concavity = [ang(circular_largest[i:i+3]) for i in range(len(largest))]
    # concavity_sign = [x < 0 for x in concavity]
    
    # if concavity_sign.count(True) > 1:
    #     return False, None, None
    
    # return True, nx.cycle_graph(largest), 2*math.pi + (0 if True not in concavity_sign else concavity[concavity_sign.index(True)])

def sphere_coord(angles):
    if len(angles) == 1:
        return np.array([np.cos(angles[0]), np.sin(angles[0])])
    return np.concatenate(([np.cos(angles[0])], sphere_coord(angles[1:])*np.sin(angles[0])), axis=0)

