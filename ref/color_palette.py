from PyQt5.QtWidgets import (
    QWidget
)

from color_palette_ui import Ui_color_palette

class ColorPalette(QWidget, Ui_color_palette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
