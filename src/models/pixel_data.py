import math
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    QRect
)
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QUndoCommand
from models.undo_stack import Validator

class PixelData(QObject):

    data_updated = pyqtSignal()
    name_updated = pyqtSignal(int, str)

    pixels_per_asset = 64
    asset_width = 8
    asset_height = 8
    assets_per_line = 16
    color_table_depth = 16

    def __init__(self):
        super().__init__()
        self.data = QImage()
        self.names = []

    def set_image(self, data, width, height):
        original_color_table = self.data.colorTable()
        self.data = QImage(data, width, height, QImage.Format_Indexed8)
        self.set_color_table(original_color_table)

    def get_image(self):
        return self.data

    def get_asset(self, asset_index):
        tiles_per_row = self.data.width() // PixelData.asset_width

        start_x = (asset_index % tiles_per_row) * PixelData.asset_width
        start_y = (asset_index // tiles_per_row) * PixelData.asset_height

        asset = QImage(PixelData.asset_width, PixelData.asset_height, QImage.Format_Indexed8)
        asset.setColorCount(PixelData.color_table_depth)
        
        for y in range(PixelData.asset_height):
            for x in range(PixelData.asset_width):
                pixel_color = self.data.pixelIndex(start_x + x, start_y + y)
                asset.setPixel(x, y, pixel_color)

        return asset

    def set_asset_names(self, names):
        self.names = names

    def set_asset_name(self, asset_index, asset_name):
        self.names[asset_index] = asset_name
        self.name_updated.emit(asset_index, asset_name)

    def get_names(self):
        return self.names

    def get_name(self, asset_index):
        return self.names[asset_index]

    def set_color_table(self, color_table):
        self.data.setColorTable(color_table)
        self.data_updated.emit()

    def set_pixels(self, new_pixels, selection):
        for y in range(selection.top(), selection.bottom()):
            for x in range(selection.left(), selection.right()):
                pixel_index = new_pixels.pixelIndex(x - selection.left(), y - selection.top())
                if pixel_index != 16:
                    self.data.setPixel(x, y, pixel_index)

        self.data_updated.emit()

    def get_pixels(self, selection):
        return self.data.copy(selection)

    def add_palette_row(self, row_data = None):
        new_image = QImage(self.data.width(), self.data.height() + 8, QImage.Format_Indexed8)
        new_image.setColorTable(self.data.colorTable())

        for y in range(new_image.height()):
            for x in range(new_image.width()):
                if y >= self.data.height():
                    if row_data is None:
                        new_image.setPixel(x, y, 0)
                    else:
                        new_image.setPixel(
                            x,
                            y,
                            row_data.pixelIndex(x, y - (new_image.height() - 8))
                        )
                else:
                    new_image.setPixel(x, y, self.data.pixelIndex(x, y))

        self.data = new_image

        self.data_updated.emit()

    def remove_palette_row(self):
        new_image = QImage(self.data.width(), self.data.height() - 8, QImage.Format_Indexed8)
        new_image.setColorTable(self.data.colorTable())
        row_image = QImage(self.data.width(), 8, QImage.Format_Indexed8)
        row_image.setColorTable(self.data.colorTable())

        for y in range(new_image.height(), self.data.height()):
            for x in range(self.data.width()):
                row_image.setPixel(x, y - (self.data.height() - 8), self.data.pixelIndex(x, y))

        for y in range(new_image.height()):
            for x in range(new_image.width()):
                new_image.setPixel(x, y, self.data.pixelIndex(x, y))

        self.data = new_image
        self.data_updated.emit()
        return row_image
    
    def to_json(self):
        image_data = []
        name_index = 0

        for y in range(0, self.data.height(), PixelData.asset_height):
            for x in range(0, self.data.width(), PixelData.asset_width):
                tile_data = []

                for row in range(PixelData.asset_height):
                    row_data = []
                    for col in range(PixelData.asset_width):
                        row_data.append(self.data.pixelIndex(x + col, y + row))
                    tile_data.append(row_data)

                asset = {
                    "name": self.names[name_index],
                    "contents": tile_data
                }
                image_data.append(asset)
                name_index += 1

        return image_data

    @staticmethod
    def parse_pixel_data(data):
        pixel_data = bytearray([0] * len(data) * PixelData.pixels_per_asset)
        names = []

        for index, palette in enumerate(data):
            names.append(palette["name"])
            col_index = math.floor(index / PixelData.assets_per_line) * PixelData.asset_width * PixelData.assets_per_line * PixelData.asset_height
            col_offset = (index % PixelData.assets_per_line) * PixelData.asset_width
            for pixel_row, pixel_row_data in enumerate(palette["contents"]):
                row_offset = pixel_row * PixelData.assets_per_line * PixelData.asset_width
                pixel_data_index = col_index + row_offset + col_offset
                pixel_data[pixel_data_index:pixel_data_index + 8] = pixel_row_data

        width = PixelData.asset_width * PixelData.assets_per_line
        height = math.ceil(len(pixel_data) / width)
        return (pixel_data, width, height, names)

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

class cmd_set_pixels(QUndoCommand):

    def __init__(self, data_source, new_pixels, selection, parent=None):
        super().__init__("set pixels", parent)
        self.data_source = data_source
        self.new_pixels = new_pixels
        scale_factor = 8
        self.selection = QRect(
            selection.x() * scale_factor,
            selection.y() * scale_factor,
            selection.width() * scale_factor + 1,
            selection.height() * scale_factor + 1
        )
        self.original_pixels = data_source.get_pixels(self.selection)

    def redo(self):
        self.data_source.set_pixels(self.new_pixels, self.selection)

    def undo(self):
        self.data_source.set_pixels(self.original_pixels, self.selection)

    def validate(self):
        return Validator(True, "")
