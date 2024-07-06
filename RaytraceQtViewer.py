import sys

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PIL import Image

from src import Raytrace, Vector, RaycastableObject, Material

class RenderWorker(QObject):
    signal_pixmap = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()

        self.scene = Raytrace.Scene()
        self.scene.add_object(
            RaycastableObject.Sphere(
                Vector.Vector3(0, 6, 5),
                5,
                Material.Material(
                    Vector.Vector3(1),
                    Vector.Vector3(1, 1, 1),
                    0
                )
            )
        )
        self.scene.add_object(RaycastableObject.Sphere(Vector.Vector3(2, -1, 5), 1, Material.Material(Vector.Vector3(0.6, 0.7, 1))))
        self.scene.add_object(RaycastableObject.Sphere(Vector.Vector3(-1, 0, 5), 1.5, Material.Material(Vector.Vector3(1, 0.7, 0.6))))

        self.camera = Raytrace.Camera(self.scene, 4, 3, 3)
        self.camera.set_parameters(1, 10)

        self._stop = False

    def pil2pixmap(self, im:Image.Image) -> QPixmap: # function to convert pil image to pyqt pixmap
        return QPixmap.fromImage(QImage(im.tobytes("raw"), im.size[0], im.size[1], QImage.Format.Format_RGB888))
    
    def vector_matrix2pixmap(self, img) -> QPixmap:
        w, h = len(img[0]), len(img)
        m = Image.new("RGB", (w, h))
        for y in range(h):
            for x in range(w):
                t = (img[y][x]*255/self.camera.render_count).to_integer().to_tuple()
                m.putpixel((x, y), t)
        return self.pil2pixmap(m)

    def run(self):
        pixmap = self.vector_matrix2pixmap(self.camera.render())
        self.signal_pixmap.emit(pixmap)
        if not self._stop:
            self.run()

    def stop(self):
        self.camera.stop()
        self._stop = True

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

        self.thread = QThread()
        self.worker = RenderWorker()
        self.worker.moveToThread(self.thread)
        self.worker.signal_pixmap.connect(self.display)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def display(self, img):
        self.canvas.setPixmap(img)

    def close(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

if __name__ == '__main__':
    App = QApplication(sys.argv)
    viewer = QtViewer()
    viewer.show()
    ret = App.exec()
    viewer.close()
    sys.exit(ret)