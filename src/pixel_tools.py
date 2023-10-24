import math
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import  QPixmap

class ToolType(Enum):
    PEN = 2

class BaseTool:
    def __init__(self, view, scene):
        self.set_scene(scene)
        self.set_view(view)

    def set_scene(self, scene):
        self.scene = scene

    def set_view(self, view):
        self.view = view

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class PenTool(BaseTool):
    def __init__(self, view, scene, color):
        super().__init__(view, scene)
        self.color = color

    def mousePressEvent(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = self.scene.sceneRect()
        if not (0 <= scene_pos.x() < scene_rect.width() and 0 <= scene_pos.y() < scene_rect.height()):
            return

        pixel_item = QGraphicsPixmapItem(QPixmap(1, 1))
        pixel_item.setPos(
            math.floor(scene_pos.x()),
            math.floor(scene_pos.y())
        )
        pixmap = QPixmap(1, 1)  # Create a new QPixmap for each pixel_item
        pixmap.fill(self.color)  # Fill the pixmap with the desired color
        pixel_item.setPixmap(pixmap)  # Set the pixmap to the pixel_item

        self.scene.addItem(pixel_item)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mousePressEvent(event)
