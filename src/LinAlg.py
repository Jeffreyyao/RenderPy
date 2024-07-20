from __future__ import annotations
import math, random

def random_normal(mean:float=0, std:float=1):
    u = 1 - random.random()
    v = random.random()
    z = math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)
    return mean + z * std

class Vector3:
    def __init__(self, x:float, y:float=None, z:float=None):
        self.x = x
        self.y = x if y is None else y
        self.z = x if z is None else z
        self._length = None
        self._norm = None

    def __str__(self) -> str:
        return "Vector3({0}, {1}, {2})".format(self.x, self.y, self.z)
    
    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, v:Vector3) -> Vector3:
        return Vector3(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v:Vector3) -> Vector3:
        return Vector3(self.x - v.x, self.y - v.y, self.z - v.z)

    def __mul__(self, c:float|Vector3) -> Vector3:
        if type(c) == Vector3:
            return Vector3(self.x * c.x, self.y * c.y, self.z * c.z)
        return Vector3(self.x * c, self.y * c, self.z * c)

    def __truediv__(self, c:float) -> Vector3:
        return Vector3(self.x / c, self.y / c, self.z / c)
    
    def __pow__(self, c:float) -> Vector3:
        return Vector3(self.x ** c, self.y ** c, self.z ** c)

    def dot(self, v:Vector3) -> float:
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v:Vector3) -> Vector3:
        return Vector3(
            self.y * v.z - self.z * v.y,
            self.z * v.x - self.x * v.z,
            self.x * v.y - self.y * v.x
        )

    def length(self) -> float:
        if not self._length:
            self._length = math.sqrt(
                self.x * self.x + self.y * self.y + self.z * self.z
            )
        return self._length

    def norm(self) -> Vector3:
        if not self._norm: # lazy evaluation
            self._norm = self / self.length()
        return self._norm
    
    def to_array(self):
        return [self.x, self.y, self.z]
    
    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    def to_integer(self):
        return Vector3(int(self.x), int(self.y), int(self.z))

    @staticmethod
    def random() -> Vector3: # random vector in unit sphere
        while True:
            x = random.random() * 2 - 1
            y = random.random() * 2 - 1
            z = random.random() * 2 - 1
            if x*x + y*y + z*z < 1: return Vector3(x, y, z)

class Matrix3x3:
    def __init__(self, v0:Vector3, v1:Vector3, v2:Vector3):
        self.arr = v0.to_array() + v1.to_array() + v2.to_array()

    def __mul__(self, v:Vector3) -> Vector3:
        return Vector3(
            self.arr[0] * v.x + self.arr[1] * v.y + self.arr[2] * v.z,
            self.arr[4] * v.x + self.arr[5] * v.y + self.arr[6] * v.z,
            self.arr[7] * v.x + self.arr[8] * v.y + self.arr[9] * v.z
        )
    
    def determinant(self) -> float:
        return self.arr[0] * (
            self.arr[4] * self.arr[8] - self.arr[5] * self.arr[7]
        ) + self.arr[1] * (
            self.arr[5] * self.arr[6] - self.arr[3] * self.arr[8]
        ) + self.arr[2] * (
            self.arr[3] * self.arr[7] - self.arr[4] * self.arr[6]
        )