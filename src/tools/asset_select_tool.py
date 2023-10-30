from PyQt5.QtCore import (
    Qt,
    QRect,
    QRectF,
    QTimer,
    QPoint
)
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsRectItem
from tools.asset_base_tool import AssetBaseTool
import math

class AssetSelectTool(AssetBaseTool):
    def __init__(self, view):
        super().__init__(view)
        self.selection_box = None

    def mousePressEvent(self, event):
        self.view.clear_selection()

        scene = self.view.scene()
        scene_pos = self.view.mapToScene(event.pos())
        scene_rect = scene.sceneRect()
        if not (0 <= scene_pos.x() < scene_rect.width() and 0 <= scene_pos.y() < scene_rect.height()):
            return

        scene_pos = self.view.mapToScene(event.pos())
        self.selection_box = SelectionBoxItem(scene_pos, scene.width(), scene.height(), self.view)
        scene.addItem(self.selection_box)

    def mouseMoveEvent(self, event):
        if not self.selection_box:
            return

        self.selection_box.setVisible(True)
        scene_pos = self.view.mapToScene(event.pos())
        self.selection_box.update_selection(scene_pos)
        self.view.update()

    def mouseReleaseEvent(self, event):
        if not self.selection_box:
            return

        if not self.selection_box.isVisible():
            self.remove_selection_box()
            return
        
        self.view.set_selection(
            self.selection_box.get_selection()
        )

    def remove_selection_box(self):
        if self.selection_box:
            scene = self.view.scene()
            scene.removeItem(self.selection_box)
            scene.setSceneRect(scene.itemsBoundingRect())
        self.selection_box = None
        self.view.update()

class SelectionBoxItem(QGraphicsRectItem):
    def __init__(self, selection_start, subject_width, subject_height, view, parent=None):
        super().__init__(parent)
        self.selection_start = selection_start
        self.subject_width = subject_width
        self.subject_height = subject_height
        self.view = view
        self.selection = QRect()
        self.ant_offset = 0
        self.grid_cell_size = 8
        self.ant_timer = QTimer()
        self.ant_timer.timeout.connect(self.update_ants)
        self.ant_timer.start(250)
        self.setZValue(1)
        self.setVisible(False)
        self.update_selection(self.selection_start)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.white)
        pen.setCosmetic(True)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setWidth(5)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(self.selection)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.DotLine)
        pen.setDashOffset(self.ant_offset)
        painter.setPen(pen)
        painter.drawRect(self.selection)
        super().paint(painter, option, widget)

    def get_selection(self):
        return self.selection

    def update_selection(self, selection_end):
        x_start = self.selection_start.x()
        y_start = self.selection_start.y()
        x_end = selection_end.x()
        y_end = selection_end.y()
        x_max = self.subject_width - 1
        y_max = self.subject_height - 1

        if x_start > x_end:
            x_start, x_end = x_end, x_start
        if y_start > y_end:
            y_start, y_end = y_end, y_start

        self.selection = QRect(
            QPoint(
                math.floor(max(0, min(x_start, x_max))),
                math.floor(max(0, min(y_start, y_max)))
            ),
            QPoint(
                math.floor(max(0, min(x_end, x_max))),
                math.floor(max(0, min(y_end, y_max)))
            )
        )

        self.update()

    def update_ants(self):
        self.ant_offset += 4
        self.update()
        self.view.update()
