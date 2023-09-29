from PyQt5.QtWidgets import (
    QWidget
)
from PyQt5.QtCore import pyqtSlot

from ui.color_palette_ui import (
    Ui_color_palette
)

class ColorPalette(QWidget, Ui_color_palette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.add_color_palette_btn.setEnabled(True)

    @pyqtSlot(str)
    def add_color_palette(self, color_palette_name):
        self.color_palette_name_combo.addItem(color_palette_name)

    @pyqtSlot(list)
    def update_palette(self, color_data):
        self.color_palette_grid.update_palette(color_data)

