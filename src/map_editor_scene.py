from math import floor, ceil
import sys
from PyQt5.QtCore import Qt, QRect, QRectF, QEvent, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QStyleOptionGraphicsItem, QGraphicsPixmapItem

class MapEditorScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subject = QImage()
        self.crop_rect = QRect()

    @pyqtSlot()
    def set_tile_map(self, tile_map):
        # Clear the existing items in the scene
        self.clear()

        # Initialize positions for placing the tiles
        x, y = 0, 0

        # Add each QImage as a QGraphicsPixmapItem to the scene
        for row in tile_map:
            for tile in row:
                pixmap = QPixmap.fromImage(tile)
                item = QGraphicsPixmapItem(pixmap)
                item.setPos(x, y)
                self.addItem(item)

                # Update the position for the next tile
                x += pixmap.width()  # Adjust as needed for spacing
            x = 0  # Reset x for the next row
            y += pixmap.height()  # Adjust as needed for spacing

    @pyqtSlot(QColor, int)
    def set_color(self, color, index):
        self.subject.setColor(index, color.rgb())

    def set_color_table(self, color_table):
        for index, color in enumerate(color_table):
            self.subject.setColor(index, color.rgb())

    def drawForeground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        rect = QRect(
            floor(rect.x()),
            floor(rect.y()),
            ceil(rect.width() + 8),
            ceil(rect.height() + 8)
        )

        # Define grid parameters
        grid_size = 8  # Adjust the size of the grid cells as needed
        grid_color = Qt.black
        grid_pen = QPen(grid_color)
        grid_pen.setWidth(0)
        
        # Set the spacing of the grid lines
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())
        
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

class Tile(QGraphicsPixmapItem):

    retrieve_tile = pyqtSignal(int)
    retrieve_color_palette = pyqtSignal(int)

    def __init__(self, pixmap=None, parent=None):
        super().__init__(pixmap, parent)
