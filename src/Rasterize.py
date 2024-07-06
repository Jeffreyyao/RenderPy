import math

class Point2D:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

class Point3D:
    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z
        self._norm_calc()
    
    def _norm_calc(self):
        self.n = math.sqrt(self.x**2+self.y**2+self.z**2)
    
    def norm(self) -> float:
        return self.n
    
    def translate(self, x:float, y:float, z:float):
        self.x += x; self.y += y; self.z += z
        self._norm_calc()
    
    def rotate(self, center, direction, angle:float):
        if not isinstance(center,Point3D):
            raise TypeError("center must be of type Point3D")
        if not isinstance(direction,Point3D):
            raise TypeError("direction must be of type Point3D")
        x,y,z = self.x-center.x,self.y-center.y,self.z-center.z
        dnorm = direction.norm()
        e1,e2,e3 = direction.x/dnorm,direction.y/dnorm,direction.z/dnorm
        c,s = math.cos(angle),math.sin(angle) # rodrigues' rotation formula
        d = (1-c)*(e1*x+e2*y+e3*z)
        r1 = c*x+s*(e2*z-e3*y)+d*e1
        r2 = c*y+s*(e3*x-e1*z)+d*e2
        r3 = c*z+s*(e1*y-e2*x)+d*e3
        self.x = r1+center.x; self.y = r2+center.y; self.z = r3+center.z

    def copy(self):
        return Point3D(self.x,self.y,self.z)
    
    def __str__(self) -> str:
        return f"Point3D({self.x},{self.y},{self.z})"

class LinAlg:
    def add(va:Point3D, vb:Point3D) -> Point3D:
        return Point3D(va.x+vb.x,va.y+vb.y,va.z+vb.z)

    def sub(va:Point3D, vb:Point3D) -> Point3D:
        return Point3D(va.x-vb.x,va.y-vb.y,va.z-vb.z)

    def scalar_mul(v:Point3D, c:float) -> Point3D:
        return Point3D(v.x*c,v.y*c,v.z*c)

    def dot(va:Point3D, vb:Point3D) -> float:
        return va.x*vb.x+va.y*vb.y+va.z*vb.z

    def cross(va:Point3D, vb:Point3D) -> Point3D:
        return Point3D(va.y*vb.z-va.z*vb.y,va.z*vb.x-va.x*vb.z,va.x*vb.y-va.y*vb.x)

class Line2D:
    def __init__(self, point1:Point2D, point2:Point2D, color="white"):
        self.point1 = point1
        self.point2 = point2
        self.color = color

class Line3D: # a line made up of two points
    def __init__(self, point1:Point3D, point2:Point3D, color="white"):
        self.point1 = point1
        self.point2 = point2
        self.color = color

    def translate(self, x:float, y:float, z:float):
        self.point1.translate(x,y,z)
        self.point2.translate(x,y,z)

    def rotate(self, center:Point3D, direction:Point3D, angle:float):
        self.point1.rotate(center,direction,angle)
        self.point2.rotate(center,direction,angle)

    def center(self) -> Point3D:
        return LinAlg.scalar_mul(LinAlg.add(self.point1,self.point2),0.5)

class Polygon2D:
    def __init__(self, points:list[Point2D], color="white"):
        self.points = points
        self.color = color

class Polygon3D: # a polygon defined by point vertices
    def __init__(self, points:list[Point3D], color="white"):
        self.points = points
        self.color = color
        self.normal = self._calc_normal()
        self.area = self._calc_area()

    def translate(self, x:float, y:float, z:float):
        for point in self.points: point.translate(x,y,z)

    def rotate(self, center:Point3D, direction:Point3D, angle:float):
        for point in self.points: point.rotate(center,direction,angle)
        self.normal = self._calc_normal()
    
    def center(self) -> Point3D: # center of mass of polygon
        sx,sy,sz,n = 0,0,0,len(self.points)
        for p in self.points: sx += p.x; sy += p.y; sz += p.z
        return Point3D(sx/n,sy/n,sz/n)

    def _calc_normal(self) -> Point3D:
        n,i = Point3D(0,0,0),0
        while n.norm()==0:
            v1 = LinAlg.sub(self.points[i+1],self.points[i])
            v2 = LinAlg.sub(self.points[i-1],self.points[i])
            n = LinAlg.cross(v1,v2)
            i += 1
        return LinAlg.scalar_mul(n,1/n.norm())

    def _calc_area(self) -> float:
        s = Point3D(0,0,0)
        v_prev = LinAlg.sub(self.points[1],self.points[0])
        for i in range(2,len(self.points)):
            v_curr = LinAlg.sub(self.points[i],self.points[0])
            s = LinAlg.scalar_mul(LinAlg.add(s,LinAlg.cross(v_prev,v_curr)),0.5)
            v_prev = v_curr
        return s.norm()

class Object: # a collection of polygons 3d and lines 3d
    def __init__(self, elements=[], center=Point3D(0,0,0)):
        self.elements = elements
        self.center =  center
    
    def translate(self, x:float, y:float, z:float):
        for elements in self.elements: elements.translate(x,y,z)
        self.center.translate(x,y,z)
    
    def rotate(self, center:Point3D, direction:Point3D, angle:float):
        for element in self.elements: element.rotate(center,direction,angle)
        center.rotate(center,direction,angle)

class Cube(Object):
    def __init__(self, size, center:Point3D=Point3D(0,0,0), facecolor="white"):
        xc,yc,zc,half = center.x,center.y,center.z,size/2
        p1 = Point3D(xc+half,yc+half,zc+half); p2 = Point3D(xc-half,yc+half,zc+half)
        p3 = Point3D(xc-half,yc-half,zc+half); p4 = Point3D(xc+half,yc-half,zc+half)
        p5 = Point3D(xc+half,yc+half,zc-half); p6 = Point3D(xc-half,yc+half,zc-half)
        p7 = Point3D(xc-half,yc-half,zc-half); p8 = Point3D(xc+half,yc-half,zc-half)
        f1 = Polygon3D([p1.copy(),p2.copy(),p3.copy(),p4.copy()],color=facecolor)
        f2 = Polygon3D([p5.copy(),p6.copy(),p2.copy(),p1.copy()],color=facecolor)
        f3 = Polygon3D([p6.copy(),p7.copy(),p3.copy(),p2.copy()],color=facecolor)
        f4 = Polygon3D([p7.copy(),p8.copy(),p4.copy(),p3.copy()],color=facecolor)
        f5 = Polygon3D([p8.copy(),p5.copy(),p1.copy(),p4.copy()],color=facecolor)
        f6 = Polygon3D([p8.copy(),p7.copy(),p6.copy(),p5.copy()],color=facecolor)
        elements = [f1,f2,f3,f4,f5,f6]
        del p1, p2, p3, p4, p5, p6, p7, p8
        super().__init__(elements,center)

class CubeOutline(Cube):
    def __init__(self, size, center:Point3D=Point3D(0,0,0), edgecolor="white"):
        xc,yc,zc,half = center.x,center.y,center.z,size/2
        p1 = Point3D(xc+half,yc+half,zc+half); p2 = Point3D(xc-half,yc+half,zc+half)
        p3 = Point3D(xc-half,yc-half,zc+half); p4 = Point3D(xc+half,yc-half,zc+half)
        p5 = Point3D(xc+half,yc+half,zc-half); p6 = Point3D(xc-half,yc+half,zc-half)
        p7 = Point3D(xc-half,yc-half,zc-half); p8 = Point3D(xc+half,yc-half,zc-half)
        l1 = Line3D(p1.copy(),p2.copy(),color=edgecolor); l2 = Line3D(p2.copy(),p3.copy(),color=edgecolor)
        l3 = Line3D(p3.copy(),p4.copy(),color=edgecolor); l4 = Line3D(p4.copy(),p1.copy(),color=edgecolor)
        l5 = Line3D(p1.copy(),p5.copy(),color=edgecolor); l6 = Line3D(p2.copy(),p6.copy(),color=edgecolor)
        l7 = Line3D(p3.copy(),p7.copy(),color=edgecolor); l8 = Line3D(p4.copy(),p8.copy(),color=edgecolor)
        l9 = Line3D(p5.copy(),p6.copy(),color=edgecolor); la = Line3D(p6.copy(),p7.copy(),color=edgecolor)
        lb = Line3D(p7.copy(),p8.copy(),color=edgecolor); lc = Line3D(p8.copy(),p5.copy(),color=edgecolor)
        elements = [l1,l2,l3,l4,l5,l6,l7,l8,l9,la,lb,lc]
        del p1, p2, p3, p4, p5, p6, p7, p8
        super().__init__(elements,center)

class WavefrontObj(Object):
    def __init__(self, filename:str, facecolor="white"):
        f = open(filename,"r"); lines = f.read().split("\n"); f.close()
        points = []
        elements = []
        for line in lines:
            l = list(filter(lambda x:x!="",line.split(" ")))
            if len(l)==0: continue
            if l[0]=="v": points.append(Point3D(float(l[1]),float(l[2]),float(l[3])))
            elif l[0]=="f":
                face_vertices = []
                for i in range(1,len(l)):
                    if l[i]=="": continue
                    index = int(l[i].split("/")[0])-1
                    face_vertices.append(points[index].copy())
                elements.append(Polygon3D(face_vertices,color=facecolor))
        print("loaded",len(elements),"polygon faces")
        sx,sy,sz = 0,0,0
        for point in points:
            sx += point.x; sy += point.y; sz += point.z
        super().__init__(elements,Point3D(sx/len(points),sy/len(points),sz/len(points)))

class WavefrontObjOutline(Object):
    def __init__(self, filename:str):
        f = open(filename,"r"); lines = f.read().split("\n"); f.close()
        points = []
        elements = []
        lines_index_set = set()
        for line in lines:
            l = list(filter(lambda x:x!="",line.split(" ",)))
            if len(l)==0: continue
            if l[0]=="v": points.append(Point3D(float(l[1]),float(l[2]),float(l[3])))
            elif l[0]=="f":
                face_vertices_index = []
                for i in range(1,len(l)):
                    if l[i]=="": continue
                    index = int(l[i].split("/")[0])-1
                    face_vertices_index.append(index)
                for i in range(len(face_vertices_index)):
                    if (i,i-1) not in lines_index_set:
                        index1,index2 = face_vertices_index[i],face_vertices_index[i-1]
                        lines_index_set.add((index1,index2))
                        lines_index_set.add((index2,index1))
                        elements.append(Line3D(points[index1].copy(),points[index2].copy()))
        sx,sy,sz = 0,0,0
        for point in points:
            sx += point.x; sy += point.y; sz += point.z
        super().__init__(elements,Point3D(sx/len(points),sy/len(points),sz/len(points)))

class Renderer:
    def __init__(self, screenx:float, screeny:float, nearz:float):
        self.screenx = screenx
        self.screeny = screeny
        self.nearz = nearz
        self.scale = 80
        self.culling_threshold = 0
        self.img_size = (screenx*self.scale,screeny*self.scale)

    def project_point3d(self, point3d:Point3D) -> Point2D:
        x = point3d.x/point3d.z*self.nearz
        y = point3d.y/point3d.z*self.nearz
        return Point2D(x,y)

    def project_line3d(self, line3d:Line3D) -> Line2D:
        return Line2D(self.project_point3d(line3d.point1),self.project_point3d(line3d.point2),line3d.color)
    
    def project_polygon3d(self, polygon3d:Polygon3D) -> Polygon2D:
        return Polygon2D([self.project_point3d(p) for p in polygon3d.points],polygon3d.color)

    def _interpolate_x(self, p_low, p_high, y:float) -> float:
        x1,y1 = p_low; x2,y2 = p_high
        return x1+(y-y1)*(x2-x1)/(y2-y1)

    def _calc_depth(self, polygon3d, i, j) -> float: # (i,j) on image pixel
        ray = ((i-self.screenx*self.scale/2)/self.scale,(j-self.screeny*self.scale/2)/self.scale,self.nearz)
        num = polygon3d.normal.x*polygon3d.points[0].x+polygon3d.normal.y*polygon3d.points[0].y+polygon3d.normal.z*polygon3d.points[0].z
        den = polygon3d.normal.x*ray[0]+polygon3d.normal.y*ray[1]+polygon3d.normal.z*ray[2]
        t = num/den
        return ray[2]*t

    def _fill_polygon(self, polygon3d, img_vertices, img, fill, depth_map):
        ymin, ymax = max(min(img_vertices,key=lambda x:x[1])[1],0), min(max(img_vertices,key=lambda x:x[1])[1],self.img_size[1])
        sides = [sorted([img_vertices[i],img_vertices[i-1]],key=lambda x:x[1]) for i in range(len(img_vertices))]
        pixels = []
        for y in range(ymin,ymax):
            x_intersects = set()
            for side in sides:
                p_low,p_high = side
                if p_low[1]<=y and y<p_high[1]:
                    if p_low[1]!=p_high[1]: x_intersects.add(self._interpolate_x(p_low,p_high,y))
                    else: x_intersects.update({side[0][0],side[1][0]})
            x_intersects = sorted(list(x_intersects))
            if len(x_intersects)%2==1: pixels.append((int(x_intersects.pop(-1)),y))
            for i in range(0,len(x_intersects),2):
                x1, x2 = max(int(x_intersects[i]),0), min(int(x_intersects[i+1]),self.img_size[0])
                for x in range(x1,x2):
                    if (depth:=self._calc_depth(polygon3d,x,y))<depth_map[y][x]:
                        pixels.append((x,y))
                        depth_map[y][x] = depth
        for pixel in pixels:
            img[pixel[1]][pixel[0]] = fill
    
    def render_object_rasterize(self, obj:Object, lighting:Point3D=None):
        img = [[0]*self.img_size[0] for _ in range(self.img_size[1])]
        depth_map = [[float("inf")]*self.img_size[0] for _ in range(self.img_size[1])]
        obj.elements.sort(key=lambda x:x.center().norm(),reverse=True) # sort polygons
        for element3d in obj.elements:
            if isinstance(element3d,Polygon3D):
                polygon2d = self.project_polygon3d(element3d)
                polygon_vertices = []
                for point in polygon2d.points:
                    x,y = int(point.x*self.scale+self.screenx*self.scale/2),int(point.y*self.scale+self.screeny*self.scale/2)
                    polygon_vertices.append((x,y))
                n = -LinAlg.dot(element3d.normal,lighting)
                d = int(255*(n*0.4+0.6))
                self._fill_polygon(element3d,polygon_vertices,img,d,depth_map) # painter's algorithm with depth buffer
            elif isinstance(element3d,Line3D):
                line2d = self.project_line3d(element3d)
                p1 = (line2d.point1.x*self.scale+self.screenx*self.scale/2,line2d.point1.y*self.scale+self.screeny*self.scale/2)
                p2 = (line2d.point2.x*self.scale+self.screenx*self.scale/2,line2d.point2.y*self.scale+self.screeny*self.scale/2)
                # draw.line([p1,p2],fill=element3d.color,width=2)
        return img

    def _polygon2d_sides(self, polygon2d:Polygon2D):
        points = polygon2d.points
        sides = [[(points[i].x,points[i].y),(points[i-1].x,points[i-1].y)] for i in range(len(points))]
        for side in sides: side.sort(key=lambda x:x[1])
        return sides

    def _point_in_polygon(self, x, y, polygon2d_sides) -> bool:
        num = 0
        for p_low,p_high in polygon2d_sides:
            if p_low[1]<=y and y<=p_high[1]:
                intersect_x = self._interpolate_x(p_low,p_high,y)
                if intersect_x>x: num += 1
        return num%2==1