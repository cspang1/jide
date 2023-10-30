from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPointF,
    QTimer
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem
)
from PyQt5.QtGui import (
    QImage,
    QPixmap,
    QPen
)
from tools.asset_base_tool import AssetBaseTool

class AssetPasteTool(AssetBaseTool):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, view):
        super().__init__(view)
        self.image = None
        self.pixmap_item = None

    def mousePressEvent(self, event):
        if not self.pixmap_item:
            return

        scene = self.view.scene()
        scene.removeItem(self.pixmap_item)
        self.pixmap_item = None

        clamped_scene_pos = self.calculate_clamped_pos(event.pos())
        paste_x = int(clamped_scene_pos.x())
        paste_y = int(clamped_scene_pos.y())

        scene_width = int(scene.width())
        scene_height = int(scene.height())
        image = QImage(
            bytearray([16] * scene_width * scene_height),
            scene_width,
            scene_height,
            QImage.Format_Indexed8
        )
        image.setColorCount(17)

        for y in range(self.image.height()):
            for x in range(self.image.width()):
                pixel_index = self.image.pixelIndex(x, y)
                if pixel_index >= 0:
                    image.setPixel(paste_x + x, paste_y + y, pixel_index)

        self.scene_edited.emit(image)
        self.view.update()

    def mouseMoveEvent(self, event):
        scene = self.view.scene()
        if self.pixmap_item:
            scene.removeItem(self.pixmap_item)

        self.image = QApplication.clipboard().image()
        self.pixmap_item = PastedImageItem(self.view, QPixmap.fromImage(self.image))
        self.pixmap_item.setPos(
            self.calculate_clamped_pos(event.pos())
        )
        scene.addItem(self.pixmap_item)
        self.view.update()

    def calculate_clamped_pos(self, pos):
        scene_rect = self.view.scene().sceneRect()
        scene_pos = self.view.mapToScene(pos)
        max_x = scene_rect.right() - self.image.width()
        max_y = scene_rect.bottom() - self.image.height()
        return QPointF(
            max(scene_rect.left(), min(int(scene_pos.x()), max_x)),
            max(scene_rect.top(), min(int(scene_pos.y()), max_y))
        ).toPoint()

    def abort_paste(self):
        if self.pixmap_item:
            self.view.scene().removeItem(self.pixmap_item)
            self.pixmap_item = None

class PastedImageItem(QGraphicsPixmapItem):
    def __init__(self, view, pixmap, parent=None):
        super().__init__(pixmap, parent)
        self.view = view
        self.ant_offset = 0
        self.ant_timer = QTimer()
        self.ant_timer.timeout.connect(self.update_ants)
        self.ant_timer.start(250)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        pen = QPen(Qt.white)
        pen.setCosmetic(True)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setWidth(5)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())
        pen.setColor(Qt.black)
        pen.setStyle(Qt.DotLine)
        pen.setDashOffset(self.ant_offset)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

    def update_ants(self):
        self.ant_offset += 4
        self.update()
        self.view.update()
