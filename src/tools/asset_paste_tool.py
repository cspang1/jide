from PyQt5.QtCore import (
    pyqtSignal,
    QPointF,
    QRect,
    QSize
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem
)
from PyQt5.QtGui import (
    QImage,
    QPixmap
)
from tools.asset_base_tool import AssetBaseTool

class AssetPasteTool(AssetBaseTool):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, view):
        super().__init__(view)
        self.pixmap_item = None

    def mousePressEvent(self, event):
        scene = self.view.scene()
        if self.pixmap_item:
            scene.removeItem(self.pixmap_item)
            self.pixmap_item = None

    def mouseMoveEvent(self, event):
        scene = self.view.scene()
        if self.pixmap_item:
            scene.removeItem(self.pixmap_item)

        scene_rect = scene.sceneRect()
        scene_pos = self.view.mapToScene(event.pos())
        image = QApplication.clipboard().image()

        clamped_scene_pos = QPointF(
            max(scene_rect.left(), min(int(scene_pos.x()), scene_rect.right() - 1)),
            max(scene_rect.top(), min(int(scene_pos.y()), scene_rect.bottom() - 1))
        ).toPoint()

        crop_rect = QRect(
            0,
            0,
            min(image.width(), int(scene_rect.width()) - clamped_scene_pos.x()),
            min(image.height(), int(scene_rect.height()) - clamped_scene_pos.y()),
        )
        image = image.copy(crop_rect)

        self.pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
        self.pixmap_item.setPos(clamped_scene_pos)
        scene.addItem(self.pixmap_item)

    def abort_paste(self):
        if self.pixmap_item:
            self.view.scene().removeItem(self.pixmap_item)
            self.pixmap_item = None

    def edits_made(self):
        # TODO
        return False
