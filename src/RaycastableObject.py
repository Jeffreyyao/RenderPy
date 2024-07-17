import abc, math, typing
from . import Material, Ray, Vector

class RaycastableObject(abc.ABC):
    def __init__(self, material=Material.Material(Vector.Vector3(1))):
        self.material = material
        self.hit_elevation = 0.0005 # elevation of ray hit point to prevent bouncing into same surface

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
        if t < 0:
            return None, None, None # hit point is behind the ray
        
        hit_point = O + D * (t - self.hit_elevation)
        hit_surface_norm = (hit_point - C).norm()
        if hit_surface_norm.dot(ray.direction) > 0:
            return None, None, None # ray is hitting surface from behind
        return t, hit_point, hit_surface_norm

class Triangle(RaycastableObject):
    def __init__(self, v0:Vector.Vector3, v1:Vector.Vector3, v2:Vector.Vector3):
        super().__init__()
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

    def hit(self, ray:Ray.Ray):
        return None

class BoundingBox(RaycastableObject):
    def __init__(self, _width, _height, _depth):
        self.width = _width
        self.height = _height
        self.depth = _depth
    
    def hit(self, ray:Ray.Ray) -> Vector.Vector3:
        return None