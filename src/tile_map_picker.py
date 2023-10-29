from PyQt5.QtWidgets import (
    QWidget,
    QInputDialog,
    QLineEdit
)
from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal
)

from views.tile_map_picker import (
    Ui_tile_map_picker
)

class TileMapPicker(QWidget, Ui_tile_map_picker):

    tile_map_changed = pyqtSignal(str)
    tile_map_added = pyqtSignal(str)
    tile_map_removed = pyqtSignal(str)
    tile_map_renamed = pyqtSignal(str, str)
    tile_map_engaged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.tile_map_name_combo.currentTextChanged.connect(self.tile_map_changed)

        self.add_tile_map_btn.pressed.connect(self.add_tile_map_dialog)
        self.rename_tile_map_btn.pressed.connect(
            lambda: self.rename_tile_map_dialog(
                self.tile_map_name_combo.currentText()
            )
        )
        self.remove_tile_map_btn.pressed.connect(
            lambda: self.tile_map_removed.emit(
                self.tile_map_name_combo.currentText()
            )
        )

    @pyqtSlot(str)
    def add_tile_map(self, tile_map_name):
        self.tile_map_name_combo.addItem(tile_map_name)
        self.tile_map_name_combo.setCurrentIndex(
            self.tile_map_name_combo.findText(tile_map_name)
        )

        # If the new palette has the same index as the current one,
        # we need to manually emit a change
        self.tile_map_name_combo.currentTextChanged.emit(
            tile_map_name
        )
        self.tile_map_engaged.emit()

    @pyqtSlot(str)
    def remove_tile_map(self, tile_map_name):
        index = self.tile_map_name_combo.findText(tile_map_name)
        self.tile_map_name_combo.removeItem(index)
        self.tile_map_engaged.emit()

    @pyqtSlot(str, str)
    def rename_tile_map(self, old_tile_map_name, new_tile_map_name):
        self.tile_map_name_combo.setItemText(
            self.tile_map_name_combo.findText(old_tile_map_name),
            new_tile_map_name
        )
        self.tile_map_name_combo.setCurrentIndex(
            self.tile_map_name_combo.findText(new_tile_map_name)
        )

        # If the renamed palette has the same index as the current one,
        # we need to manually emit a change
        self.tile_map_name_combo.currentTextChanged.emit(
            new_tile_map_name
        )
        self.tile_map_engaged.emit()

    @pyqtSlot()
    def add_tile_map_dialog(self):
        name, accepted = QInputDialog.getText(
            self, "Add Tile Map", "Tile Map name:", QLineEdit.Normal, "new_tile_map"
        )
        if accepted:
            self.tile_map_added.emit(name)

    @pyqtSlot(str)
    def rename_tile_map_dialog(self, old_tile_map_name):
        new_map_name, accepted = QInputDialog.getText(
            self, "Rename Tile Map", "Tile Map name:", QLineEdit.Normal, old_tile_map_name
        )
        if accepted:
            self.tile_map_renamed.emit(old_tile_map_name, new_map_name)

    def get_current_map_name(self):
        return self.tile_map_name_combo.currentText()
