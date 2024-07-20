from . import LinAlg

class Material:
    def __init__(self, color:LinAlg.Vector3, emission_color=LinAlg.Vector3(0), emission_strength=0.0):
        self.color = color
        self.emission_color = emission_color
        self.emission_strength = emission_strength
        self.emission = emission_color * emission_strength