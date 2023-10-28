from PyQt5.QtCore import QRect, QRectF, Qt, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem
from base_tool import BaseTool
import math

class SelectTool(BaseTool):
    def __init__(self, view):
        super().__init__(view)
        self.selection_box = None

    def mousePressEvent(self, event):
        self.remove_selection_box()

        scene_pos = self.view.mapToScene(event.pos())
        scene = self.view.scene()
        self.selection_box = SelectionBoxItem(scene_pos, scene.width(), scene.height())
        scene.addItem(self.selection_box)
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        self.selection_box.update_selection(scene_pos)
        self.view.update()

    def mouseReleaseEvent(self, event):
        self.view.set_selection(self.selection_box.get_selection())

    def remove_selection_box(self):
        self.selection_box = None
        self.view.set_selection(None)
        scene = self.view.scene()
        for item in scene.items():
            if isinstance(item, SelectionBoxItem):
                scene.removeItem(item)
                return

class SelectionBoxItem(QGraphicsItem):
    def __init__(self, selection_start, subject_width, subject_height, parent=None):
        super().__init__(parent)
        self.selection_start = selection_start
        self.selection_end = selection_start
        self.subject_width = subject_width
        self.subject_height = subject_height
        self.selection = QRect()
        self.ant_offset = 0
        self.grid_cell_size = 8

        self.ant_timer = QTimer()
        self.ant_timer.timeout.connect(self.update_ants)
        self.ant_timer.start(250)

        self.setZValue(1)

    def boundingRect(self):
        return QRectF(self.selection)

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
