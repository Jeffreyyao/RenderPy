from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PIL import Image

import numpy as np

import sys, src.Rasterize as Rasterize, math, time

class QtViewer(QWidget):
    def __init__(self, obj_filename=None):
        super().__init__()

        self.canvas = QLabel()
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.hbox.addStretch()
        self.hbox.addWidget(self.canvas)
        self.hbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        
        if obj_filename is None:
            self.obj = Rasterize.Cube(2)
        else:
            self.obj = Rasterize.WavefrontObj(obj_filename)
            self.setWindowTitle(obj_filename)
        self.obj.translate(0,0,5)
        self.obj.rotate(self.obj.center,Rasterize.Point3D(1,0,0),math.pi)
        self.obj.rotate(self.obj.center,Rasterize.Point3D(0,1,0),math.pi/3)
        self.renderer = Rasterize.Renderer(6,4,5)
        self.lighting = Rasterize.Point3D(1,0,0)
        self.render()

        self.increment_step = 0.15
        self.mouse_press_pos = None

    def render(self):
        # self.canvas.setPixmap(self.pil2pixmap(img = self.renderer.render_object_rasterize(self.obj,self.lighting)))
        self.canvas.setPixmap(self.matrix2pixmap(self.renderer.render_object_rasterize(self.obj,self.lighting)))

    def keyPressEvent(self, e:QKeyEvent):
        if e.key()==Qt.Key.Key_Escape: quit()
        elif e.key()==Qt.Key.Key_Left: self.obj.translate(-self.increment_step,0,0)
        elif e.key()==Qt.Key.Key_Right: self.obj.translate(self.increment_step,0,0)
        elif e.key()==Qt.Key.Key_Up: self.obj.translate(0,-self.increment_step,0)
        elif e.key()==Qt.Key.Key_Down: self.obj.translate(0,self.increment_step,0)
        elif e.key()==Qt.Key.Key_Equal: self.obj.translate(0,0,-self.increment_step)
        elif e.key()==Qt.Key.Key_Minus: self.obj.translate(0,0,self.increment_step)
        self.render()

    def mousePressEvent(self, event:QMouseEvent):
        self.mouse_press_pos = (event.pos().x(),event.pos().y())

    def arcball_vector(self, x, y):
        P = Rasterize.Point3D(1*x/self.renderer.img_size[0]*2-1.0, 1.0*y/self.renderer.img_size[1]*2-1, 0)
        P.x = -P.x; P.y = -P.y
        OP_squared = P.x * P.x + P.y * P.y
        if OP_squared <= 1*1:
            P.z = math.sqrt(1*1 - OP_squared)
        else:
            P_norm = P.norm()
            P = Rasterize.Point3D(P.x/P_norm,P.y/P_norm,P.z/P_norm)
        return P

    def mouseMoveEvent(self, event:QMouseEvent):
        if self.mouse_press_pos:
            # arcball rotation https://en.wikibooks.org/wiki/OpenGL_Programming/Modern_OpenGL_Tutorial_Arcball
            va = self.arcball_vector(self.mouse_press_pos[0],self.mouse_press_pos[1])
            self.mouse_press_pos = (event.pos().x(),event.pos().y())
            vb = self.arcball_vector(self.mouse_press_pos[0],self.mouse_press_pos[1])
            angle = math.acos(min(1.0, va.x*vb.x+va.y*vb.y+va.z*vb.z))
            axis = Rasterize.Point3D(va.y*vb.z-va.z*vb.y,va.z*vb.x-va.x*vb.z,va.x*vb.y-va.y*vb.x)
            if not (axis.norm()==0):
                # print(f"self.obj.rotate(self.obj.center,Py3D.{axis.__str__()},{angle})")
                self.obj.rotate(self.obj.center,axis,angle)
                self.render()

    def mouseReleaseEvent(self, event:QMouseEvent):
        self.mouse_press_pos = None
    
    def pil2pixmap(self, im:Image.Image) -> QPixmap: # function to convert pil image to pyqt pixmap
        return QPixmap.fromImage(QImage(im.tobytes("raw","L"),im.size[0],im.size[1],QImage.Format.Format_Grayscale8))
    
    def matrix2pixmap(self, img) -> QPixmap:
        m = Image.fromarray(np.uint8(np.array(img)))
        return self.pil2pixmap(m)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    if len(sys.argv)==1:
        window = QtViewer()
    else:
        window = QtViewer(sys.argv[1])
    window.show()
    sys.exit(App.exec())
