from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    qAlpha
)
from PyQt5.QtCore import (
    pyqtSignal,
    QRectF,
    QPoint
)
from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QPen
)
from PyQt5.QtCore import Qt
from tools.base_tool import BaseTool

class RectangleTool(BaseTool):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, view):
        super().__init__(view)
        self.pixmap = None
        self.pixmap_item = None
        self.color = None
        self.color_index = None
        self.start_point = None
        self.end_point = None

    def mousePressEvent(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = self.view.scene().sceneRect()
        self.pixmap = QPixmap(
            int(scene_rect.width()),
            int(scene_rect.height())
        )
        self.pixmap.fill(Qt.transparent)
        self.start_point = QPoint(
            int(scene_pos.x()),
            int(scene_pos.y())
        )
        self.end_point = QPoint(
            int(scene_pos.x()),
            int(scene_pos.y())
        )
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_point is None:
            return

        self.pixmap.fill(Qt.transparent)

        scene_pos = self.view.mapToScene(event.pos())
        self.end_point = QPoint(
            int(scene_pos.x()),
            int(scene_pos.y())
        )
        painter = QPainter(self.pixmap)
        pen = QPen(self.color)
        painter.setPen(pen)
        painter.setClipRect(
            self.view.get_selection() or self.view.scene().sceneRect()
        )
        painter.setBrush(self.color)
        painter.drawRect(
            QRectF(self.start_point, self.end_point).normalized().toRect()
        )

        scene = self.view.scene()
        if self.pixmap_item:
            scene.removeItem(self.pixmap_item)
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        scene.addItem(self.pixmap_item)

    def mouseReleaseEvent(self, event):
        if self.start_point is None:
            return

        scene = self.view.scene()
        scene.removeItem(self.pixmap_item)
        scene.setSceneRect(scene.itemsBoundingRect())
        self.pixmap_item = None
        self.start_point = None

        if not self.edits_made():
            return

        image = QImage(self.pixmap.size(), QImage.Format_Indexed8)
        image.setColorCount(17)
        image.setColor(self.color_index, self.color.rgb())

        for y in range(self.pixmap.height()):
            for x in range(self.pixmap.width()):
                pixel = self.pixmap.toImage().pixel(x, y)
                if pixel == self.color.rgb():
                    image.setPixel(x, y, self.color_index)
                else:
                    image.setPixel(x, y, 16)

        self.scene_edited.emit(image)


    def edits_made(self):
        for y in range(self.pixmap.height()):
            for x in range(self.pixmap.width()):
                pixel = self.pixmap.toImage().pixel(x, y)
                alpha = qAlpha(pixel)
                if alpha != 0:
                    return True

        return False

    def set_color(self, color, color_index):
        self.color = color
        self.color_index = color_index
