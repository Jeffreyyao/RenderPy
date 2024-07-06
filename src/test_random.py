import matplotlib.pyplot as plt

from Vector import Vector3 as v3

a = []

for _ in range(100000):
    a.append(v3.random().x)

plt.hist(a)
plt.show()