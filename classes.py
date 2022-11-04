from scipy.special import *
class ParticleInPolygon:
    def __init__(self, polygon, mass) -> None:
        self.polygon = polygon
        self.mass = mass
        