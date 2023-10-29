from collections import OrderedDict
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QUndoCommand
from models.undo_stack import Validator

class ColorData(QObject):

    color_palette_added = pyqtSignal(str)
    color_palette_removed = pyqtSignal(str)
    color_palette_renamed = pyqtSignal(str, str)
    color_updated = pyqtSignal(str, QColor, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_data = OrderedDict()

    @pyqtSlot(str, list)
    def add_color_palette(self, color_palette_name, color_palette_data):
        self.color_data[color_palette_name] = color_palette_data
        self.color_palette_added.emit(color_palette_name)

    @pyqtSlot(str)
    def remove_color_palette(self, color_palette_name):
        del self.color_data[color_palette_name]
        self.color_palette_removed.emit(color_palette_name)

    @pyqtSlot(str, str)
    def rename_color_palette(self, old_color_palette_name, new_color_palette_name):
        color_palette_data = self.color_data[old_color_palette_name]
        del self.color_data[old_color_palette_name]
        self.color_data[new_color_palette_name] = color_palette_data
        self.color_palette_renamed.emit(old_color_palette_name, new_color_palette_name)

    @pyqtSlot(str)
    def get_color_palette(self, color_palette_name):
        return self.color_data[color_palette_name]

    def get_color_palette_name(self, color_palette_index):
        return list(self.color_data.keys())[color_palette_index]

    @pyqtSlot(str, QColor, int)
    def update_color(self, color_palette_name, color, index):
        self.color_data[color_palette_name][index] = color
        self.color_updated.emit(color_palette_name, color, index)

    def get_color_data(self):
        return self.color_data

    def to_json(self):
        color_data = []

        for color_palette_name, color_palette in self.color_data.items():
            colors = []
            for color in color_palette:
                r, g, b = ColorData.downsample(color.red(), color.green(), color.blue())
                color = (r << 5) | (g << 2) | b
                colors.append(color)

            palette = {
                "name": color_palette_name,
                "contents": colors
            }
            
            color_data.append(palette)

        return color_data
    
    @staticmethod
    def upsample(red, green, blue):
        red = round((red / 7) * 255)
        green = round((green / 7) * 255)
        blue = round((blue / 3) * 255)
        return (red, green, blue)

    @staticmethod
    def downsample(red, green, blue):
        red = round((red / 255) * 7)
        green = round((green / 255) * 7)
        blue = round((blue / 255) * 3)
        return (red, green, blue)

    @staticmethod
    def normalize(red, green, blue):
        return ColorData.upsample(*ColorData.downsample(red, green, blue))

    @staticmethod
    def parse_color_data(data):
        for palette in data:
            cur_pal = palette["contents"]
            cur_pal[:] = [
                QColor(*ColorData.upsample(color >> 5, (color >> 2) & 7, color & 3))
                for color in cur_pal
            ]
            yield (palette["name"], cur_pal)

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
