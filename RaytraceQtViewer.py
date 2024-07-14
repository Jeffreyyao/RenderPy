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
                Vector.Vector3(2, -1, 3),
                1,
                Material.Material(
                    Vector.Vector3(1),
                    Vector.Vector3(1, 1, 1),
                    1
                )
            )
        )
        self.scene.add_object(RaycastableObject.Sphere(Vector.Vector3(0, 6, 5), 5, Material.Material(Vector.Vector3(0.6, 0.7, 1))))
        self.scene.add_object(RaycastableObject.Sphere(Vector.Vector3(-1, 0, 5), 1.5, Material.Material(Vector.Vector3(1, 0.7, 0.6))))

        self.camera = Raytrace.Camera(self.scene, 5, 3, 3)
        self.camera.set_parameters(1, 10)

        self._stop = False

    def pil2pixmap(self, im:Image.Image) -> QPixmap: # function to convert pil image to pyqt pixmap
        return QPixmap.fromImage(QImage(im.tobytes("raw"), im.size[0], im.size[1], QImage.Format.Format_RGB888))
    
    def vector_matrix2pixmap(self, img) -> QPixmap:
        w, h = len(img[0]), len(img)
        m = Image.new("RGB", (w, h))
        for y in range(h):
            for x in range(w):
                t = (img[y][x]*256).to_integer().to_tuple()
                m.putpixel((x, y), t)
        return self.pil2pixmap(m)

    def run(self):
        self.camera.render()
        pixmap = self.vector_matrix2pixmap(self.camera.get_img(0.5))
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
        self.label_render_count = QLabel()
        self.hbox = QHBoxLayout()
        self.hbox.addStretch()
        self.hbox.addWidget(self.canvas)
        self.hbox.addStretch()
        self.button_save = QPushButton("Save Image")
        self.button_save.clicked.connect(self.save)
        self.vbox.addWidget(self.label_render_count)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.button_save)
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)

        self.thread = QThread()
        self.worker = RenderWorker()
        self.worker.moveToThread(self.thread)
        self.worker.signal_pixmap.connect(self.display)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.render_count = 0
        self.img = QPixmap()

    def display(self, img):
        self.render_count += 1
        self.label_render_count.setText(f"Render count: {self.render_count}")
        self.img = img
        self.canvas.setPixmap(img)

    def save(self):
        self.img.save("output.png")

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