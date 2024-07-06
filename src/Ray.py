from . import Vector

class Ray:
    def __init__(self, origin:Vector.Vector3, direction:Vector.Vector3):
        self.origin = origin
        self.direction = direction.norm()

    def set_direction(self, direction:Vector.Vector3):
        self.direction = direction.norm()

    def __str__(self):
        return "Ray({0}, {1})".format(self.origin, self.direction)