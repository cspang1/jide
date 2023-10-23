from PyQt5.QtWidgets import (
    QUndoCommand,
    QUndoStack
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from collections import namedtuple

Validator = namedtuple('Validator', ['is_valid', 'validation_error'])
class UndoStack(QUndoStack):

    error_thrown = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def push(self, command):
        is_valid, validation_error = command.validate()
        if is_valid:
            super().push(command)
        else:
            if validation_error:
                self.error_thrown.emit(validation_error)

class cmd_set_color(QUndoCommand):

    def __init__(self, data_source, palette_name, update_color, update_index, parent=None):
        super().__init__("set palette color", parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.update_index = update_index
        self.update_color = update_color
        self.original_color = self.data_source.get_color_palette(palette_name)[update_index]

    def redo(self):
        self.data_source.update_color(self.palette_name, self.update_color, self.update_index)

    def undo(self):
        self.data_source.update_color(self.palette_name, self.original_color, self.update_index)

    def validate(self):
        return Validator(True, "")

class cmd_rename_color_palette(QUndoCommand):

    def __init__(self, data_source, old_palette_name, new_palette_name, parent=None):
        super().__init__("rename color palette", parent)
        self.data_source = data_source
        self.old_palette_name = old_palette_name
        self.new_palette_name = new_palette_name

    def redo(self):
        self.data_source.rename_color_palette(self.old_palette_name, self.new_palette_name)

    def undo(self):
        self.data_source.rename_color_palette(self.new_palette_name, self.old_palette_name)

    def validate(self):
        if self.old_palette_name == self.new_palette_name:
            return Validator(False, "")
        if self.new_palette_name in self.data_source.get_color_data():
            return Validator(False, "A color palette with that name already exists")
        if not self.new_palette_name:
            return Validator(False, "Color palette name cannot be blank")

        return Validator(True, "")

class cmd_add_color_palette(QUndoCommand):

    def __init__(self, data_source, palette_name, palette_contents=[QColor(255, 0, 255)] * 16, parent=None):
        super().__init__("add  color palette", parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.palette_contents = palette_contents

    def redo(self):
        self.data_source.add_color_palette(self.palette_name, self.palette_contents)

    def undo(self):
        self.data_source.remove_color_palette(self.palette_name)

    def validate(self):
        if not self.palette_name:
            return Validator(False, "Color palette name cannot be blank")
        if self.palette_name in self.data_source.get_color_data():
            return Validator(False, "A color palette with that name already exists")

        return Validator(True, "")

class cmd_remove_color_palette(QUndoCommand):

    def __init__(self, data_source, palette_name, parent=None):
        super().__init__("remove color palette", parent)
        self.data_source = data_source
        self.palette_name = palette_name
        self.original_contents = self.data_source.get_color_palette(palette_name)

    def redo(self):
        self.data_source.remove_color_palette(self.palette_name)

    def undo(self):
        self.data_source.add_color_palette(self.palette_name, self.original_contents)

    def validate(self):
        if len(self.data_source.get_color_data()) == 1:
            return Validator(False, "At least one color palette is required")
        
        return Validator(True, "")

class cmd_add_pixel_palette_row(QUndoCommand):

    def __init__(self, data_source, parent=None):
        super().__init__("add pixel palette row", parent)
        self.data_source = data_source

    def redo(self):
        self.data_source.add_palette_row()

    def undo(self):
        self.data_source.remove_palette_row()

    def validate(self):
        return Validator(True, "")

class cmd_remove_pixel_palette_row(QUndoCommand):

    def __init__(self, data_source, parent=None):
        super().__init__("remove pixel palette row", parent)
        self.data_source = data_source
        self.removed_row = None

    def redo(self):
        self.removed_row = self.data_source.remove_palette_row()

    def undo(self):
        self.data_source.add_palette_row(self.removed_row)

    def validate(self):
        if self.data_source.get_image().height() <= 8:
            return Validator(False, "At least one row of assets is required")

        return Validator(True, "")

class cmd_set_asset_name(QUndoCommand):

    def __init__(self, data_source, asset_index, new_asset_name, parent=None):
        super().__init__("set asset name", parent)
        self.data_source = data_source
        self.asset_index = asset_index
        self.new_asset_name = new_asset_name
        self.old_asset_name = self.data_source.get_name(self.asset_index)

    def redo(self):
        self.data_source.set_asset_name(self.asset_index, self.new_asset_name)

    def undo(self):
        self.data_source.set_asset_name(self.asset_index, self.old_asset_name)

    def validate(self):
        if self.old_asset_name == self.new_asset_name:
            return Validator(False, "")
        if self.new_asset_name in self.data_source.get_names():
            return Validator(False, "An asset with that name already exists")
        if not self.new_asset_name:
            return Validator(False, "Asset name cannot be blank")

        return Validator(True, "")

class cmd_add_tile_map(QUndoCommand):

    def __init__(self, data_source, tile_map_name, tile_map_contents=[0, 0] * 40 * 30, parent=None):
        super().__init__("add tile map", parent)
        self.data_source = data_source
        self.tile_map_name = tile_map_name
        self.tile_map_contents = tile_map_contents

    def redo(self):
        self.data_source.add_tile_map(self.tile_map_name, self.tile_map_contents)

    def undo(self):
        self.data_source.remove_tile_map(self.tile_map_name)

    def validate(self):
        if not self.tile_map_name:
            return Validator(False, "Tile map name cannot be blank")
        if self.tile_map_name in self.data_source.get_tile_maps():
            return Validator(False, "A tile map with that name already exists")

        return Validator(True, "")
