import math
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    qRgba
)
from PyQt5.QtCore import pyqtSignal
from tools.base_tool import BaseTool

class PenTool(BaseTool):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.pixmap = None
        self.color = None
        self.color_index = None

    def mousePressEvent(self, event):
        scene = self.view.scene()
        scene_rect = scene.sceneRect()
        width = math.floor(scene_rect.width())
        height = math.floor(scene_rect.height())
        data = bytearray([16] * width * height)
        self.image = QImage(data, width, height, QImage.Format_Indexed8)
        self.image.setColorCount(17)
        self.image.setColor(16, qRgba(0, 0, 0, 0))
        self.image.setColor(self.color_index, self.color.rgb())
        self.pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        self.pixmap.setPos(0, 0)
        self.view.scene().addItem(self.pixmap)
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        scene = self.view.scene()
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = scene.sceneRect()
        selection_rect = self.view.get_selection()
        x_limit = selection_rect.x() if selection_rect else 0
        y_limit = selection_rect.y() if selection_rect else 0
        width_limit = selection_rect.width() + x_limit if selection_rect else scene_rect.width()
        height_limit = selection_rect.height() + y_limit if selection_rect else scene_rect.height()
        if not (x_limit <= scene_pos.x() < width_limit and y_limit <= scene_pos.y() < height_limit):
            return

        x, y = math.floor(scene_pos.x()), math.floor(scene_pos.y())
        self.image.setPixel(x, y, self.color_index)
        updated_pixmap = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        updated_pixmap.setPos(0, 0)
        scene.removeItem(self.pixmap)
        self.pixmap = updated_pixmap
        scene.addItem(self.pixmap)

    def mouseReleaseEvent(self, event):
        scene = self.view.scene()
        scene.removeItem(self.pixmap)
        scene.setSceneRect(scene.itemsBoundingRect())
        if self.edits_made():
            self.scene_edited.emit(self.image)

    def edits_made(self):
        for y in range(self.image.height()):
            for x in range(self.image.width()):
                pixel_index = self.image.pixelIndex(x, y)
                if pixel_index != 16:
                    return True

        return False

    def set_color(self, color, color_index):
        self.color = color
        self.color_index = color_index
