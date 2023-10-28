import math
from PyQt5.QtCore import (
    Qt,
    QRect,
    pyqtSlot
)
from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QImage,
    QColor,
    QPen
)
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsPixmapItem
)

class AssetEditorScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subject = QImage()
        self.crop_rect = QRect()

    @pyqtSlot(QRect)
    def select_cells(self, crop_rect):
        scale_factor = 8
        x = crop_rect.x() * scale_factor
        y = crop_rect.y() * scale_factor
        width = crop_rect.width() * scale_factor
        height = crop_rect.height() * scale_factor
        cropped_image = self.subject.copy(QRect(x, y, width, height))
        self.crop_rect = crop_rect
        self.clear()
        self.addItem(QGraphicsPixmapItem(QPixmap.fromImage(cropped_image)))
        self.setSceneRect(self.itemsBoundingRect())

    @pyqtSlot()
    def set_scene_image(self, subject):
        self.subject = subject
        self.select_cells(self.crop_rect)

    @pyqtSlot(QColor, int)
    def set_color(self, color, index):
        self.subject.setColor(index, color.rgb())
        self.select_cells(self.crop_rect)

    def set_color_table(self, color_table):
        for index, color in enumerate(color_table):
            self.subject.setColor(index, color.rgb())
        self.select_cells(self.crop_rect)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        # painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRect(
            math.floor(rect.x()),
            math.floor(rect.y()),
            math.ceil(rect.width() + 8),
            math.ceil(rect.height() + 8)
        )

        # Define grid parameters
        grid_size = 8
        grid_color = QColor(0, 0, 0, 128)
        grid_pen = QPen(grid_color)
        grid_pen.setWidth(0)

        # Define 1x1 pixel grid parameters
        small_grid_size = 1
        small_grid_color = QColor(192, 192, 192, 128)
        small_grid_pen = QPen(small_grid_color)
        small_grid_pen.setWidth(0)
        
        # Set the spacing of the grid lines
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())
        
        # Draw vertical small grid lines
        x = left - (left % small_grid_size)
        while x <= right:
            painter.setPen(small_grid_pen)
            painter.drawLine(x, top, x, bottom)
            x += small_grid_size
            
        # Draw horizontal small grid lines
        y = top - (top % small_grid_size)
        while y <= bottom:
            painter.setPen(small_grid_pen)
            painter.drawLine(left, y, right, y)
            y += small_grid_size

        # Draw vertical grid lines
        x = left - (left % grid_size)
        while x <= right:
            painter.setPen(grid_pen)
            painter.drawLine(x, top, x, bottom)
            x += grid_size
            
        # Draw horizontal grid lines
        y = top - (top % grid_size)
        while y <= bottom:
            painter.setPen(grid_pen)
            painter.drawLine(left, y, right, y)
            y += grid_size
