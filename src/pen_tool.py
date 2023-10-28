import math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    qRgba
)
from base_tool import BaseTool

class PenTool(BaseTool):
    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.pixmap = None

    def mousePressEvent(self, event):
        scene = self.view.scene()
        scene_rect = scene.sceneRect()

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
        self.view.scene().addItem(self.pixmap)
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        scene = self.view.scene()
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = scene.sceneRect()
        if not (0 <= scene_pos.x() < scene_rect.width() and 0 <= scene_pos.y() < scene_rect.height()):
            return

        x, y = math.floor(scene_pos.x()), math.floor(scene_pos.y())
        self.image.setPixel(x, y, 1)
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        updated_pixmap.setPos(0, 0)
        scene.removeItem(self.pixmap)
        self.pixmap = updated_pixmap
        scene.addItem(self.pixmap)

    def mouseReleaseEvent(self, event):
        self.image = None
        self.view.scene().removeItem(self.pixmap)
