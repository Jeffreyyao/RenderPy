import abc, math
from . import LinAlg, Material, Ray

class RayHitInfo:
    def __init__(self, t : float,
        hit_point : LinAlg.Vector3,
        hit_normal : LinAlg.Vector3,
        hit_object : "RaycastableObject"
    ):
        self.t = t
        self.hit_point = hit_point
        self.hit_normal = hit_normal
        self.hit_object = hit_object

    def __bool__(self):
        return self.t < math.inf
    
    def __repr__(self):
        return f"t: {self.t}; hit_point: {str(self.hit_point)}; hit_normal: {str(self.hit_normal)}"
    
    def empty() -> "RayHitInfo":
        return RayHitInfo(math.inf, None, None, None)
    
class RaycastableObject(abc.ABC):
    def __init__(self, material:Material.Material=None):
        if material is None:
            self.material = Material.Material(LinAlg.Vector3(1))
        else:
            self.material = material
        self.epsilon = 0.0005 # number <= this considered as 0

    @abc.abstractmethod
    def hit(self, ray:Ray.Ray) -> RayHitInfo:
        pass

    def set_material(self, material:Material.Material):
        self.material = material

class Sphere(RaycastableObject):
    def __init__(self, center:LinAlg.Vector3, radius:float, material:Material.Material=None):
        super().__init__(material)
        self.center = center
        self.radius = radius

    def hit(self, ray:Ray.Ray) -> RayHitInfo:
        C = self.center
        O = ray.origin
        D = ray.direction

        a = D.dot(D)
        b = 2*O.dot(D) - 2*C.dot(D)
        c = O.dot(O) + C.dot(C) - 2*O.dot(C) - self.radius**2

        delta = b**2 - 4*a*c
        if delta < 0: return RayHitInfo.empty()

        t1 = (-b - math.sqrt(delta)) / (2 * a)
        t2 = (-b + math.sqrt(delta)) / (2 * a)
        t = [t1, t2][not t1 > 0]
        if t < 0:
            return RayHitInfo.empty() # hit point is behind the ray
        
        hit_point = ray.eval(t - self.epsilon) # elevate hit point by epsilon
        hit_surface_norm = (hit_point - C).norm()
        if hit_surface_norm.dot(ray.direction) > 0:
            return RayHitInfo.empty() # ray is hitting surface from behind
        return RayHitInfo(t, hit_point, hit_surface_norm, self)

class Triangle(RaycastableObject):
    def __init__(self, v0:LinAlg.Vector3, v1:LinAlg.Vector3, v2:LinAlg.Vector3, material:Material.Material=None):
        super().__init__(material)
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.edge1 = self.v1 - self.v0
        self.edge2 = self.v2 - self.v0
        self.normal = self.edge1.cross(self.edge2).norm()

    def hit(self, ray:Ray.Ray) -> RayHitInfo:
        if ray.direction.dot(self.normal) >= -self.epsilon:
            return RayHitInfo.empty() # ray direction must be opposite to normal
        
        # O + D*t = v0 + c1*edge1 + c2*edge2 => find t, c1, c2
        # => [-D; edge1; edge2][t; c1; c2] = [O - v0]
        det = LinAlg.Matrix3x3(
            ray.direction * -1, self.edge1, self.edge2
        ).determinant()
        c1 = LinAlg.Matrix3x3(
            ray.direction * -1, ray.origin - self.v0, self.edge2
        ).determinant() / det
        if c1 < 0 or c1 > 1:
            return RayHitInfo.empty() # constraint on c1
        c2 = LinAlg.Matrix3x3(
            ray.direction * -1, self.edge1, ray.origin - self.v0
        ).determinant() / det
        if c2 < 0 or c1 + c2 > 1:
            return RayHitInfo.empty() # constraint on c1, c2
        
        t = LinAlg.Matrix3x3(
            ray.origin - self.v0, self.edge1, self.edge2
        ).determinant() / det
        hit_point = ray.eval(t - self.epsilon)
        return RayHitInfo(t, hit_point, self.normal, self)
    
class Parallelogram(RaycastableObject): # formed by two mirrored Triangles
    def __init__(self, v0:LinAlg.Vector3, v1:LinAlg.Vector3, v2:LinAlg.Vector3, material:Material.Material=None):
        super().__init__()
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

        self.center = (v1 + v2) * 0.5
        self.v3 = self.center - self.v0 + self.center
        self.triangle1 = Triangle(v0, v1, v2, material)
        self.triangle2 = Triangle(v1, self.v3, v2, material)

    def hit(self, ray:Ray.Ray) -> RayHitInfo:
        if hit_info1 := self.triangle1.hit(ray): return hit_info1
        if hit_info2 := self.triangle2.hit(ray): return hit_info2
        return RayHitInfo.empty()

class Box(RaycastableObject):
    def __init__(self, center:LinAlg.Vector3, width:float, height:float, depth:float):
        super().__init__()
        self.center = center
        self.width = width
        self.height = height
        self.depth = depth
    
    def hit(self, ray:Ray.Ray) -> RayHitInfo:
        pass