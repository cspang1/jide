from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot, 
    QRect,
) 
from ui.pixel_palette_ui import Ui_pixel_palette

class PixelPalette(QWidget, Ui_pixel_palette):

    assets_selected = pyqtSignal(QRect)
    add_palette_row = pyqtSignal()
    remove_palette_row = pyqtSignal()
    pixel_palette_engaged = pyqtSignal()
    asset_renamed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pixel_palette_grid.assets_selected.connect(self.assets_selected)
        self.pixel_palette_grid.asset_renamed.connect(self.asset_renamed)
        self.add_palette_row_btn.pressed.connect(self.add_palette_row)
        self.remove_palette_row_btn.pressed.connect(self.remove_palette_row)
        self.vertical_layout.setAlignment(Qt.AlignTop)

    def set_pixel_palette(self, pixel_palette_data):
        self.pixel_palette_grid.set_pixel_palette(pixel_palette_data)
        self.pixel_palette_engaged.emit()

    def set_asset_name(self, asset_index, new_asset_name):
        self.pixel_palette_grid.set_asset_name(asset_index, new_asset_name)
        self.pixel_palette_engaged.emit()

    def set_color_table(self, color_table):
        self.pixel_palette_grid.set_color_table(color_table)

    def set_selection(self, selection):
        self.pixel_palette_grid.set_selection(selection)

    @pyqtSlot(QColor, int)
    def set_color(self, color, index):
        self.pixel_palette_grid.set_color(color, index)
