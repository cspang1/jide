from PyQt5.QtWidgets import (
    QWidget
)
from PyQt5.QtCore import pyqtSlot

from source import Source
from color import Color
from ui.color_palette_ui import (
    Ui_color_palette
)
from color_picker_dialog import ColorPickerDialog

class ColorPalette(QWidget, Ui_color_palette):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.palette = [Color(n, Source.SPRITE) for n in range(16)]
        positions = [(row, col) for row in range(4) for col in range(4)]
        for position, color in zip(positions, self.palette):
            # color.color_selected.connect(self.selectColor)
            # color.edit.connect(self.openPicker)
            self.color_layout.addWidget(color, *position)

        self.add_color_palette_btn.setEnabled(True)
        self.add_color_palette_btn.clicked.connect(self.open_color_picker)

    @pyqtSlot(str)
    def add_color_palette(self, color_palette_name):
        self.color_palette_name_combo.addItem(color_palette_name)

    def open_color_picker(self):
        color_picker = ColorPickerDialog()
        color_picker.exec()
