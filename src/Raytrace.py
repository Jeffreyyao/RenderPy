import math, random, time, typing
from . import Ray, RaycastableObject, Vector

class Scene:
    def __init__(self):
        self.objects:typing.List[RaycastableObject.RaycastableObject] = []
    
    def get_background(self, D:Vector.Vector3):
        ratio = D.y / math.sqrt(D.x**2 + D.z**2)
        if ratio > 10: return Vector.Vector3(0)
        c = 1 / (1 + math.exp(ratio)) * 0.3
        return Vector.Vector3(c)
    
    def add_object(self, obj:RaycastableObject.RaycastableObject):
        self.objects.append(obj)

class Camera:
    def __init__(self, scene:Scene, width:float, height:float, depth:float):
        self.scene = scene
        self.width = width # world camera plane width
        self.height = height # world camera plane height
        self.depth = depth # world camera plane depth
        self.scene_pixel_scale = 100 # pixels per world unit
        self.rays_per_pixel = 10
        self.max_reflections = 3

        self.width_pixels = int(self.width * self.scene_pixel_scale)
        self.height_pixels = int(self.height * self.scene_pixel_scale)
        self.img = [[Vector.Vector3(0)]*self.width_pixels for _ in range(self.height_pixels)]

        self.render_count = 0
        self.render_time = []

        self._stop = False

    def set_parameters(self, rays_per_pixel, max_reflections):
        self.rays_per_pixel = rays_per_pixel
        self.max_reflections = max_reflections

    def ray_color(self, r:Ray.Ray, reflections:int):
        if reflections == 0: return self.scene.get_background(r.direction)

        hitinfo_min = RaycastableObject.RayHitInfo.empty()
        for obj in self.scene.objects:
            hitinfo = obj.hit(r)
            if hitinfo.t < hitinfo_min.t:
                hitinfo_min = hitinfo

        if hitinfo_min:
            if hitinfo_min.hit_object.material.emission_strength > 0:
                if reflections == self.max_reflections:
                    return hitinfo_min.hit_object.material.color
                return hitinfo_min.hit_object.material.emission
            reflection = Vector.Vector3.random().norm()
            if reflection.dot(hitinfo_min.hit_normal) < 0:
                reflection *= -1
            return self.ray_color(
                Ray.Ray(hitinfo_min.hit_point, reflection),
                reflections - 1
            ) * hitinfo_min.hit_object.material.color * 2 * hitinfo_min.hit_normal.dot(reflection)
        
        return self.scene.get_background(r.direction)

    def render(self): # can be called multiple times for averaged trayces
        self.render_count += 1
        self._stop = False
        render_time_start = time.time()

        total_iterations = self.width_pixels * self.height_pixels
        for x in range(self.width_pixels):
            for y in range(self.height_pixels):
                if self._stop: return self.img
                print(f'percentage complete: {int((x*self.height_pixels + y) / total_iterations * 100)}%', end='\r')
                ray = Ray.Ray(
                    Vector.Vector3(0),
                    Vector.Vector3(
                        x / self.scene_pixel_scale - self.width / 2,
                        y / self.scene_pixel_scale - self.height / 2,
                        self.depth
                    )
                )
                for _ in range(self.rays_per_pixel):
                    vec_noise = Vector.Vector3(
                        (random.random() - 0.5) * 0.0003,
                        (random.random() - 0.5) * 0.0003,
                        0
                    )
                    ray.set_direction(ray.direction + vec_noise)
                    self.img[y][x] += self.ray_color(ray, self.max_reflections) / self.rays_per_pixel
        
        self.render_time.append(time.time() - render_time_start)
        print("\nrender complete")

    def get_img(self, gamma:float=1):
        img_result = [[Vector.Vector3(0)]*self.width_pixels for _ in range(self.height_pixels)]
        for x in range(self.width_pixels):
            for y in range(self.height_pixels):
                img_result[y][x] = (self.img[y][x] / self.render_count) ** gamma
        return img_result

    def stop(self):
        self._stop = True

    def save_to_ppm(self, filename:str="output.ppm"):
        with open(filename, 'w') as f:
            f.write(f'P3\n{self.width_pixels} {self.height_pixels}\n255')
            for y in range(self.height_pixels):
                f.write('\n')
                for x in range(self.width_pixels):
                    c = self.img[y][x] / self.rays_per_pixel
                    f.write(f'{int(c.x*255)} {int(c.y*255)} {int(c.z*255)} ')
