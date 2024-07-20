from . import LinAlg

class Ray:
    def __init__(self, origin:LinAlg.Vector3, direction:LinAlg.Vector3):
        self.origin = origin
        self.direction = direction.norm()

    def set_direction(self, direction:LinAlg.Vector3):
        self.direction = direction.norm()
    
    def eval(self, t:float):
        return self.origin + self.direction * t

    def __str__(self):
        return "Ray({0}, {1})".format(self.origin, self.direction)