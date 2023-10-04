from PyQt5.QtGui import QPixmap, QKeySequence, QColor, QImage
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QGraphicsScene
)

from source import Source
from color import Color
from ui.pixel_palette_ui import Ui_pixel_palette

class PixelPalette(QWidget, Ui_pixel_palette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def set_pixel_palette(self, pixel_palette_data):
        self.pixel_palette_grid.set_pixel_palette(pixel_palette_data)
