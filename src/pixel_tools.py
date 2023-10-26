import math
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import  QPixmap, QImage, qRgba, QColor

class ToolType(Enum):
    NONE = 0
    SELECT = 1
    PEN = 2
    FILL = 3
    LINE = 4
    RECTANGLE = 5
    ELLIPSE = 6

class BaseTool:
    def __init__(self, view):
        self.set_view(view)
        self.scene = None
        self.color = None

    def set_scene(self, scene):
        self.scene = scene

    def set_view(self, view):
        self.view = view

    def set_color(self, color):
        self.color = color

    def mousePressEvent(self, event): pass

    def mouseMoveEvent(self, event): pass

    def mouseReleaseEvent(self, event): pass

class PenTool(BaseTool):
    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.pixmap = None

    def mousePressEvent(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = self.scene.sceneRect()
        if not (0 <= scene_pos.x() < scene_rect.width() and 0 <= scene_pos.y() < scene_rect.height()):
            return

        if not self.image:
            width = math.floor(scene_rect.width())
            height = math.floor(scene_rect.height())
            data = bytearray([0] * width * height)
            self.image = QImage(data, width, height, QImage.Format_Indexed8)
            self.image.setColorTable([
                qRgba(0, 0, 0, 0),
                self.color.rgba()
            ])
            self.pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
            self.pixmap.setPos(0, 0)
            self.scene.addItem(self.pixmap)

        x, y = math.floor(scene_pos.x()), math.floor(scene_pos.y())
        self.image.setPixel(x, y, 1)
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        updated_pixmap.setPos(0, 0)
        self.scene.removeItem(self.pixmap)
        self.pixmap = updated_pixmap
        self.scene.addItem(self.pixmap)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.image = None
        self.scene.removeItem(self.pixmap)

class SelectTool(BaseTool):
    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.pixmap = None

    def mousePressEvent(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = self.scene.sceneRect()
        if not (0 <= scene_pos.x() < scene_rect.width() and 0 <= scene_pos.y() < scene_rect.height()):
            return

        if not self.image:
            width = math.floor(scene_rect.width())
            height = math.floor(scene_rect.height())
            data = bytearray([1] * width * height)
            self.image = QImage(data, width, height, QImage.Format_Indexed8)
            self.image.setColorTable(
                [QColor("red").rgba(),
                 qRgba(0, 0, 0, 0)]
            )
            self.pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
            self.pixmap.setPos(0, 0)
            self.scene.addItem(self.pixmap)

        x, y = math.floor(scene_pos.x()), math.floor(scene_pos.y())
        self.image.setPixel(x, y, 0)
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        updated_pixmap.setPos(0, 0)
        self.scene.removeItem(self.pixmap)
        self.pixmap = updated_pixmap
        self.scene.addItem(self.pixmap)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.image = None
        self.scene.removeItem(self.pixmap)