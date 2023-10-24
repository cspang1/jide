from math import floor, ceil
import sys
from PyQt5.QtCore import Qt, QRect, QRectF, QEvent, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QStyleOptionGraphicsItem, QGraphicsPixmapItem
from collections import namedtuple

class MapEditorScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subject = QImage()
        self.crop_rect = QRect()
        self.tile_map_images = []

    @pyqtSlot()
    def set_tile_map(self, tile_map_images):
        self.tile_map_images = tile_map_images
        self.refresh_tile_map()

    def refresh_tile_map(self):
        self.clear()
        x, y = 0, 0
        for row in self.tile_map_images:
            for tile in row:
                pixmap = QPixmap.fromImage(tile)
                item = QGraphicsPixmapItem(pixmap)
                item.setPos(x, y)
                self.addItem(item)
                x += pixmap.width()

            x = 0
            y += pixmap.height()

        self.setSceneRect(self.itemsBoundingRect())

    @pyqtSlot(str, QColor, int)
    def set_color(self, color_palette, color, index):
        for tile in [tile for row in self.tile_map_images for tile in row]:
            if tile.color_palette_name == color_palette:
                tile.setColor(index, color.rgb())

        self.refresh_tile_map()

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

class RenderedTile(QImage):

    def __init__(self, tile_image, color_palette_name, tile_palette_index):
        super().__init__(tile_image)
        self.color_palette_name = color_palette_name
        self.tile_palette_index = tile_palette_index

    @staticmethod
    def render_tile_map(tile_map_data, color_palette_data, tile_palette_data):
        map_height = tile_map_data.get_height()
        map_width = tile_map_data.get_width()
        tile_map_images = [[None for _ in range(map_width)] for _ in range(map_height)]
        for row in range(map_height):
            for col in range(map_width):
                tile = tile_map_data.get_tile(col, row)
                color_palette_index = tile.color_palette_index
                tile_palette_index = tile.tile_palette_index
                tile_image = tile_palette_data.get_asset(tile_palette_index)
                color_palette_name = color_palette_data.get_color_palette_name(color_palette_index)
                color_palette = color_palette_data.get_color_palette(color_palette_name)
                tile_image.setColorTable([color.rgb() for color in color_palette])
                tile_map_images[row][col] = RenderedTile(tile_image, color_palette_name, tile_palette_index)

        return tile_map_images
