from PyQt5.QtGui import QPixmap, QKeySequence, QColor, QImage
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QGraphicsScene
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot, 
    QRegExp,
    QEvent, 
    QRect,
    QPoint,
    QSize
) 
from ui.pixel_palette_ui import Ui_pixel_palette

class PixelPalette(QWidget, Ui_pixel_palette):

    elements_selected = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pixel_palette_grid.elements_selected.connect(self.elements_selected)

    def set_pixel_palette(self, pixel_palette_data):
        self.pixel_palette_grid.set_pixel_palette(pixel_palette_data)

    def set_color_table(self, color_table):
        self.pixel_palette_grid.set_color_table(color_table)

    @pyqtSlot(QColor, int)
    def set_color(self, color, index):
        self.pixel_palette_grid.set_color(color, index)
