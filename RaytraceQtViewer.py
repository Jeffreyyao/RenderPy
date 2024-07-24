import sys

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PIL import Image

from src import LinAlg, Material, Raytrace, RaycastableObject

def scene_circles(scene:Raytrace.Scene):
    scene.add_object(
        RaycastableObject.Sphere(
            LinAlg.Vector3(2, -1, 3),
            1,
            Material.Material(
                LinAlg.Vector3(0.8),
                LinAlg.Vector3(1, 1, 1),
                1
            )
        )
    )
    scene.add_object(RaycastableObject.Sphere(LinAlg.Vector3(0, 6, 5), 5, Material.Material(LinAlg.Vector3(0.6, 0.7, 1))))
    scene.add_object(RaycastableObject.Sphere(LinAlg.Vector3(-1, 0, 5), 1.5, Material.Material(LinAlg.Vector3(1, 0.7, 0.6))))

def scene_cube(scene:Raytrace.Scene):
    scene.add_object(
        RaycastableObject.Sphere(
            LinAlg.Vector3(0.5, 0, 3),
            0.6,
            Material.Material(
                LinAlg.Vector3(0.9),
                LinAlg.Vector3(1, 1, 1),
                1
            )
        )
    )
    p000 = LinAlg.Vector3(0, 0, 0) + LinAlg.Vector3(-2, 0.5, 4)
    p001 = LinAlg.Vector3(0, 0, 1) + LinAlg.Vector3(-2, 0.5, 4)
    p010 = LinAlg.Vector3(0, 1, 0) + LinAlg.Vector3(-2, 0.5, 4)
    p011 = LinAlg.Vector3(0, 1, 1) + LinAlg.Vector3(-2, 0.5, 4)
    p100 = LinAlg.Vector3(1, 0, 0) + LinAlg.Vector3(-2, 0.5, 4)
    p101 = LinAlg.Vector3(1, 0, 1) + LinAlg.Vector3(-2, 0.5, 4)
    p110 = LinAlg.Vector3(1, 1, 0) + LinAlg.Vector3(-2, 0.5, 4)
    p111 = LinAlg.Vector3(1, 1, 1) + LinAlg.Vector3(-2, 0.5, 4)

    blue = Material.Material(LinAlg.Vector3(0.6, 0.7, 1))
    scene.add_object(RaycastableObject.Parallelogram(p111, p101, p110, blue))
    scene.add_object(RaycastableObject.Parallelogram(p110, p100, p010, blue))
    scene.add_object(RaycastableObject.Parallelogram(p101, p001, p100, blue))
    # scene.add_object(RaycastableObject.Parallelogram(p111, p110, p011, blue))
    # scene.add_object(RaycastableObject.Parallelogram(p111, p011, p101, blue))
    # scene.add_object(RaycastableObject.Parallelogram(p001, p011, p000, blue))

class RenderResult:
    def __init__(self, pixmap:QPixmap, render_count:int, spf:float):
        self.pixmap = pixmap
        self.render_count = render_count
        self.spf = spf

class RenderWorker(QObject):
    signal_render_result = pyqtSignal(RenderResult)

    def __init__(self):
        super().__init__()

        self.scene = Raytrace.Scene()
        # scene_circles(self.scene)
        scene_cube(self.scene)

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
        pixmap = self.vector_matrix2pixmap(self.camera.get_img())
        self.signal_render_result.emit(RenderResult(
            pixmap,
            self.camera.render_count,
            sum(self.camera.render_time) / self.camera.render_count
        ))
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
        self.worker.signal_render_result.connect(self.display_result)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.img = QPixmap()

    def display_result(self, render_result:RenderResult):
        self.label_render_count.setText(f"Render count: {render_result.render_count}; Avg spf: {'%.2f'%render_result.spf}")
        self.img = render_result.pixmap
        self.canvas.setPixmap(render_result.pixmap)

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