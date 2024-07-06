import abc, math, typing
from . import Material, Ray, Vector

class RaycastableObject(abc.ABC):
    def __init__(self, material=Material.Material(Vector.Vector3(1))):
        self.material = material

    @abc.abstractmethod
    def hit(self, ray:Ray.Ray) -> typing.Tuple[float, Vector.Vector3, Vector.Vector3]:
        pass

    def set_material(self, material:Material.Material):
        self.material = material

class Sphere(RaycastableObject):
    def __init__(self, center:Vector.Vector3, radius:float, material=Material.Material(Vector.Vector3(1))):
        super().__init__(material)
        self.center = center
        self.radius = radius

    def hit(self, ray:Ray.Ray):
        C = self.center
        O = ray.origin
        D = ray.direction

        a = D.dot(D)
        b = 2*O.dot(D) - 2*C.dot(D)
        c = O.dot(O) + C.dot(C) - 2*O.dot(C) - self.radius**2

        delta = b**2 - 4*a*c
        if delta < 0: return None, None, None

        t1 = (-b - math.sqrt(delta)) / (2 * a)
        t2 = (-b + math.sqrt(delta)) / (2 * a)
        t = [t1, t2][not t1 > 0]
        if t < 0: return None, None, None # hit point is behind the ray
        hit_point = O + D * t
        return t, hit_point, (hit_point - C).norm()

class Triangle(RaycastableObject):
    def __init__(self, v0:Vector.Vector3, v1:Vector.Vector3, v2:Vector.Vector3):
        super().__init__()
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

    def hit(self, ray:Ray.Ray):
        E1 = self.v1 - self.v0
        E2 = self.v2 - self.v0
        P = ray.direction.cross(E2)
        det = E1.dot(P)
        if det > -1e-6 and det < 1e-6: return None
        inv_det = 1.0 / det
        T = ray.origin - self.v0
        u = T.dot(P) * inv_det
        if u < 0 or u > 1: return None
        Q = T.cross(E1)
        v = ray.direction.dot(Q) * inv_det
        if v < 0 or u + v > 1: return None
        t = E2.dot(Q) * inv_det
        if t > 1e-6: return t
        return None

class BoundingBox(RaycastableObject):
    def __init__(self, _width, _height, _depth):
        self.width = _width
        self.height = _height
        self.depth = _depth
    
    def hit(self, ray:Ray.Ray) -> Vector.Vector3:
        return None