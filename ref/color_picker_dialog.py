from PyQt5.QtWidgets import (
    QDialog
)

from source import Source
from color import Color
from ui.color_picker_dialog_ui import Ui_color_picker_dialog

class ColorPickerDialog(QDialog, Ui_color_picker_dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
