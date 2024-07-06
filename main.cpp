#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <SDL2/SDL_timer.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <set>
#include <sstream>
#include <string>
#include <vector>

class Point2D {
 public:
  double x, y;

  Point2D() {
    x = 0;
    y = 0;
  }

  Point2D(double xc, double yc) {
    x = xc;
    y = yc;
  }
};

class Point3D {
 private:
  void _norm_calc() {
    n = std::sqrt(std::pow(x, 2) + std::pow(y, 2) + std::pow(z, 2));
  }

 public:
  double x, y, z, n;
  
  Point3D() {
    x = 0;
    y = 0;
    z = 0;
    _norm_calc();
  }

  Point3D(double xc, double yc, double zc) {
    x = xc;
    y = yc;
    z = zc;
    _norm_calc();
  }

  double norm() {
    return n;
  }

  void translate(double xt, double yt, double zt) {
    x += xt;
    y += yt;
    z += zt;
    _norm_calc();
  }

  void rotate(Point3D &center, Point3D &direction, double angle) {
    x -= center.x;
    y -= center.y;
    z -= center.z;
    double dnorm = direction.norm();
    double e1 = direction.x / dnorm;
    double e2 = direction.y / dnorm;
    double e3 = direction.z / dnorm;
    double c = std::cos(angle);
    double s = std::sin(angle);
    double d = (1 - c) * (e1 * x + e2 * y + e3 * z);
    double r1 = c * x + s * (e2 * z - e3 * y) + d * e1;
    double r2 = c * y + s * (e3 * x - e1 * z) + d * e2;
    double r3 = c * z + s * (e1 * y - e2 * x) + d * e3;
    x = r1 + center.x;
    y = r2 + center.y;
    z = r3 + center.z;
  }

  Point3D copy() { return Point3D(x, y, z); }

  std::string toString() {
    return "Point3D(" + std::to_string(x) + ", " + std::to_string(y) + ", " +
           std::to_string(z) + ")";
  }
};

class LinAlg {
 public:
  static Point3D add(Point3D &va, Point3D &vb) {
    return Point3D(va.x + vb.x, va.y + vb.y, va.z + vb.z);
  }

  static Point3D sub(Point3D &va, Point3D &vb) {
    return Point3D(va.x - vb.x, va.y - vb.y, va.z - vb.z);
  }

  static Point3D scalar_mul(Point3D &v, double c) {
    return Point3D(v.x * c, v.y * c, v.z * c);
  }

  static double dot(Point3D &va, Point3D &vb) {
    return va.x * vb.x + va.y * vb.y + va.z * vb.z;
  }

  static Point3D cross(Point3D &va, Point3D &vb) {
    return Point3D(va.y * vb.z - va.z * vb.y, va.z * vb.x - va.x * vb.z,
                   va.x * vb.y - va.y * vb.x);
  }
};

class Polygon2D {
 public:
  std::vector<Point2D> points;
  std::string color;

  Polygon2D(std::vector<Point2D> &pointsc, std::string color) {
    points = pointsc;
    color = color;
  }
};

class Polygon3D {
 public:
  std::vector<Point3D> points;
  std::string color;
  Point3D normal;

  Polygon3D(std::vector<Point3D> &pointsc, std::string colorc = "white") {
    points = pointsc;
    color = colorc;
    normal = _normal();
  }

  void translate(double x, double y, double z) {
    for (Point3D &point : points) {
      point.translate(x, y, z);
    }
  }

  void rotate(Point3D &center, Point3D &direction, double angle) {
    for (Point3D &point : points) {
      point.rotate(center, direction, angle);
    }
    normal = _normal();
  }

  Point3D center() {
    double sx = 0, sy = 0, sz = 0;
    int n = points.size();
    for (Point3D &point : points) {
      sx += point.x;
      sy += point.y;
      sz += point.z;
    }
    return Point3D(sx / n, sy / n, sz / n);
  }

 private:
  Point3D _normal() {
    Point3D n(0, 0, 0);
    int i = 1;
    while (n.norm() == 0) {
      Point3D v1 = LinAlg::sub(points[i + 1], points[i]);
      Point3D v2 = LinAlg::sub(points[i - 1], points[i]);
      n = LinAlg::cross(v1, v2);
      i++;
    }
    return LinAlg::scalar_mul(n, 1 / n.norm());
  }
};

class Object {
 public:
  std::vector<Polygon3D> polygons;
  Point3D center;

  Object() {}

  Object(std::vector<Polygon3D> &polygonsc) { polygons = polygonsc; }

  Object(std::vector<Polygon3D> &polygonsc, Point3D &centerc) {
    polygons = polygonsc;
    center = centerc;
  }

  void translate(double x, double y, double z) {
    for (Polygon3D &polygon : polygons) {
      polygon.translate(x, y, z);
    }
    center.translate(x, y, z);
  }

  void rotate(Point3D &center, Point3D &direction, double angle) {
    for (Polygon3D &polygon : polygons) {
      polygon.rotate(center, direction, angle);
    }
    center.rotate(center, direction, angle);
  }
};

class Cube : public Object {
 public:
  Cube(double size, Point3D &centerc, std::string facecolor = "black") {
    double xc = centerc.x, yc = centerc.y, zc = centerc.z, half = size / 2;
    Point3D p1 = Point3D(xc + half, yc + half, zc + half);
    Point3D p2 = Point3D(xc - half, yc + half, zc + half);
    Point3D p3 = Point3D(xc - half, yc - half, zc + half);
    Point3D p4 = Point3D(xc + half, yc - half, zc + half);
    Point3D p5 = Point3D(xc + half, yc + half, zc - half);
    Point3D p6 = Point3D(xc - half, yc + half, zc - half);
    Point3D p7 = Point3D(xc - half, yc - half, zc - half);
    Point3D p8 = Point3D(xc + half, yc - half, zc - half);

    std::vector<Point3D> v1{p1.copy(), p2.copy(), p3.copy(), p4.copy()};
    std::vector<Point3D> v2{p5.copy(), p6.copy(), p2.copy(), p1.copy()};
    std::vector<Point3D> v3{p6.copy(), p7.copy(), p3.copy(), p2.copy()};
    std::vector<Point3D> v4{p7.copy(), p8.copy(), p4.copy(), p3.copy()};
    std::vector<Point3D> v5{p8.copy(), p5.copy(), p1.copy(), p4.copy()};
    std::vector<Point3D> v6{p8.copy(), p7.copy(), p6.copy(), p5.copy()};
    Polygon3D f1 = Polygon3D(v1, facecolor);
    Polygon3D f2 = Polygon3D(v2, facecolor);
    Polygon3D f3 = Polygon3D(v3, facecolor);
    Polygon3D f4 = Polygon3D(v4, facecolor);
    Polygon3D f5 = Polygon3D(v5, facecolor);
    Polygon3D f6 = Polygon3D(v6, facecolor);

    center = centerc;
    polygons.insert(polygons.end(), {f1, f2, f3, f4, f5, f6});
  }
};

class WaveforontObj : public Object {
 public:
  WaveforontObj(std::string filename) {
    center = Point3D(0, 0, 0);
    std::ifstream file(filename);
    std::vector<Point3D> points;
    for (std::string line; getline(file, line);) {
      std::vector<std::string> l = split(line, ' ');
      if (l.size() == 0) {
        continue;
      }
      if (l[0] == "v") {
        points.push_back(
            Point3D(std::stod(l[1]), std::stod(l[2]), std::stod(l[3])));
      } else if (l[0] == "f") {
        std::vector<Point3D> face_vertices;
        for (int i = 1; i < l.size(); i++) {
          if (l[i] == "") {
            continue;
          }
          int index = std::stoi(split(l[i], '/')[0]) - 1;
          face_vertices.push_back(points[index].copy());
        }
        polygons.push_back(Polygon3D(face_vertices));
      }
    }
  }

 private:
  std::vector<std::string> split(std::string text, char delim) {
    std::string temp;
    std::vector<std::string> vec;
    std::stringstream ss(text);
    while (getline(ss, temp, delim)) {
      if (temp != "") {
        vec.push_back(temp);
      }
    }
    return vec;
  }
};

class Renderer {
 public:
  double screenx, screeny, nearz;
  int scale, img_w, img_h;

  Renderer() {}

  Renderer(double _screenx, double _screeny, double _nearz, int _scale,
           int _img_w, int _img_h) {
    screenx = _screenx;
    screeny = _screeny;
    nearz = _nearz;
    scale = _scale;
    img_w = _img_w;
    img_h = _img_h;
  }

  void render(SDL_Renderer *renderer, Object &obj, Point3D &lighting) {
    std::sort(obj.polygons.begin(), obj.polygons.end(), sort_polygon);
    std::reverse(obj.polygons.begin(), obj.polygons.end());
    for (Polygon3D polygon3d : obj.polygons) {
      Polygon2D polygon2d = project_polygon3d(polygon3d);
      double n = -LinAlg::dot(polygon3d.normal, lighting);
      int color = (int)(255 * (n * 0.4 + 0.6));
      fill_polygon(renderer, polygon2d, color);
    }
  }

 private:
  static bool sort_polygon(Polygon3D &p1, Polygon3D &p2) {
    return p1.center().norm() < p2.center().norm();
  }

  Point2D project_point3d(Point3D &p) {
    double x = p.x / p.z * nearz;
    double y = p.y / p.z * nearz;
    return Point2D(x, y);
  }

  Polygon2D project_polygon3d(Polygon3D &polygon3d) {
    std::vector<Point2D> points2d;
    for (Point3D &point3d : polygon3d.points) {
      points2d.push_back(project_point3d(point3d));
    }
    return Polygon2D(points2d, polygon3d.color);
  }

  int interpolate_x(double x_low, double y_low, double x_high, double y_high,
                    double y) {
    return (int)(x_low + (y - y_low) * (x_high - x_low) / (y_high - y_low));
  }

  void fill_polygon(SDL_Renderer *renderer, Polygon2D &polygon2d, int color) {
    SDL_SetRenderDrawColor(renderer, color, color, color, 255);
    int ymin = std::numeric_limits<int>::max();
    int ymax = std::numeric_limits<int>::min();
    std::vector<std::vector<int>> sides;
    for (int i = 0; i < polygon2d.points.size(); i++) {
      int j = i - 1;
      if (j < 0) {
        j = polygon2d.points.size() - 1;
      }
      Point2D p1 = polygon2d.points[i];
      int x1 = (int)(p1.x * scale + screeny * scale / 2);
      int y1 = (int)(p1.y * scale + screeny * scale / 2);
      Point2D p2 = polygon2d.points[j];
      int x2 = (int)(p2.x * scale + screeny * scale / 2);
      int y2 = (int)(p2.y * scale + screeny * scale / 2);
      ymin = std::min(ymin, y1);
      ymax = std::max(ymax, y1);
      std::vector<int> side;
      if (y1 < y2) {
        side.insert(side.end(), {x1, y1, x2, y2});
      } else {
        side.insert(side.end(), {x2, y2, x1, y1});
      }
      sides.push_back(side);
    }
    ymin = std::max(ymin, 0);
    ymax = std::min(ymax, img_h);
    for (int y = 0; y < ymax; y++) {
      std::set<int> x_intersects_set;
      for (std::vector<int> side : sides) {
        int x_low = side[0];
        int y_low = side[1];
        int x_high = side[2];
        int y_high = side[3];
        if (y_low <= y && y < y_high) {
          if (y_low != y_high) {
            x_intersects_set.insert(
                interpolate_x(x_low, y_low, x_high, y_high, y));
          } else {
            x_intersects_set.insert(x_low);
            x_intersects_set.insert(x_high);
          }
        }
      }
      // no need to sort x_intersects because c++ auto sorts int sets.
      std::vector<int> x_intersects(x_intersects_set.begin(),
                                    x_intersects_set.end());
      if (x_intersects.size() % 2 == 1) {
        SDL_RenderDrawPoint(renderer, x_intersects[x_intersects.size() - 1], y);
        x_intersects.pop_back();
      }
      for (int i = 0; i < x_intersects.size(); i += 2) {
        int x1 = std::max(x_intersects[i], 0);
        int x2 = std::min(x_intersects[i + 1], img_w);
        for (int x = x1; x < x2; x++) {
          SDL_RenderDrawPoint(renderer, x, y);
        }
      }
    }
  }
};

int main(int argc, char *argv[]) {
  int width = 400;
  int height = 300;
  SDL_Event event;
  SDL_Renderer *renderer;
  SDL_Window *window;
  SDL_Init(SDL_INIT_VIDEO);
  SDL_CreateWindowAndRenderer(width, height, 0, &window, &renderer);
  SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0);
  SDL_RenderClear(renderer);

  Point3D c(0, 0, 0);
  Point3D lighting(-1, 0, 0);
  Renderer r(5, 5, 5, 60, width, height);

  WaveforontObj obj = WaveforontObj("objects/plane.obj");
  if (argc == 2) {
    obj = WaveforontObj(argv[1]);
  }
  
  Point3D center(0, 0, 0);
  Point3D direction1(0, 0, 1);
  obj.rotate(center, direction1, 3.14);
  Point3D direction2(0, 1, 0);
  obj.rotate(center, direction2, -3.14/4);
  obj.translate(0.4, 0, 3.8);

  while (1) {
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0);
    SDL_RenderClear(renderer);
    r.render(renderer, obj, lighting);
    SDL_RenderPresent(renderer);
    SDL_Delay(1);
    if (SDL_PollEvent(&event) && event.type == SDL_QUIT) {
      break;
    }
  }
  SDL_DestroyRenderer(renderer);
  SDL_DestroyWindow(window);
  SDL_Quit();
  return EXIT_SUCCESS;
}