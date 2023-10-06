from PyQt5.QtWidgets import (
    QWidget,
    QInputDialog,
    QLineEdit
)
from PyQt5.QtGui import QColor, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from ui.color_palette_ui import (
    Ui_color_palette
)

class ColorPalette(QWidget, Ui_color_palette):

    color_changed = pyqtSignal(QColor, int)
    color_palette_changed = pyqtSignal(str)
    color_palette_added = pyqtSignal(str)
    color_palette_removed = pyqtSignal(str)
    color_palette_renamed = pyqtSignal(str, str)
    color_previewed = pyqtSignal(QColor, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.color_palette_name_combo.currentTextChanged.connect(self.color_palette_changed)
        self.color_palette_grid.primary_color_selected.connect(self.color_preview.set_primary_color)
        self.color_palette_grid.secondary_color_selected.connect(self.color_preview.set_secondary_color)
        self.color_palette_grid.primary_color_changed.connect(self.color_preview.set_primary_color)
        self.color_palette_grid.primary_color_changed.connect(self.color_changed)
        self.color_palette_grid.color_previewed.connect(self.color_previewed)

        self.color_preview.switch_color.pressed.connect(self.color_palette_grid.swap_colors)
        self.add_color_palette_btn.pressed.connect(self.add_color_palette_dialog)
        self.rename_color_palette_btn.pressed.connect(
            lambda: self.rename_color_palette_dialog(
                self.color_palette_name_combo.currentText()
            )
        )
        self.remove_color_palette_btn.pressed.connect(
            lambda: self.color_palette_removed.emit(
                self.color_palette_name_combo.currentText()
            )
        )

    @pyqtSlot(str)
    def add_color_palette(self, color_palette_name):
        self.color_palette_name_combo.addItem(color_palette_name)

    @pyqtSlot(str)
    def remove_color_palette(self, color_palette_name):
        index = self.color_palette_name_combo.findText(color_palette_name)
        self.color_palette_name_combo.removeItem(index)

    @pyqtSlot(str, str)
    def rename_color_palette(self, old_color_palette_name, new_color_palette_name):
        index = self.color_palette_name_combo.findText(old_color_palette_name)
        self.color_palette_name_combo.setItemText(index, new_color_palette_name)

    @pyqtSlot(list)
    def change_palette(self, color_data):
        for index, color in enumerate(color_data):
            self.color_palette_grid.set_color(color, index)
        self.color_palette_grid.select_primary_color(0)
        self.color_palette_grid.select_secondary_color(0)

    @pyqtSlot(QColor, int)
    def update_color(self, color, index):
        self.color_palette_grid.set_color(color, index)

    @pyqtSlot()
    def add_color_palette_dialog(self, event=None):
        name, accepted = QInputDialog.getText(
            self, "Add Palette", "Palette name:", QLineEdit.Normal, "new_palette"
        )
        if accepted:
            self.color_palette_added.emit(name)

    @pyqtSlot(str)
    def rename_color_palette_dialog(self, old_palette_name, event=None):
        new_palette_name, accepted = QInputDialog.getText(
            self, "Rename Palette", "Palette name:", QLineEdit.Normal, old_palette_name
        )
        if accepted:
            self.color_palette_renamed.emit(old_palette_name, new_palette_name)

    def get_current_palette_name(self):
        return self.color_palette_name_combo.currentText()
