from PyQt5.QtWidgets import (
    QWidget, QLabel
)

from source import Source
from color import Color
from pixel_palette_ui import Ui_pixel_palette

class PixelPalette(QWidget, Ui_pixel_palette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
