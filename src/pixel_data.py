import math
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QImage
from history import(
    cmdAddPixelRow,
    cmdRemovePixelRow,
    cmdSetAssetName
)

class PixelData(QObject):

    data_updated = pyqtSignal()
    name_updated = pyqtSignal(int, str)
    error_thrown = pyqtSignal(str)

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

        # Calculate the starting pixel coordinates of the specified tile
        start_x = (asset_index % tiles_per_row) * PixelData.asset_width
        start_y = (asset_index // tiles_per_row) * PixelData.asset_height

        # Create a new QImage for the tile
        asset = QImage(PixelData.asset_width, PixelData.asset_height, QImage.Format_Indexed8)
        asset.setColorCount(PixelData.color_table_depth)
        
        # Copy the pixel data from the original image to the tile image
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

    @pyqtSlot()
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

    @pyqtSlot()
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

        # Iterate through the image, dividing it into tiles
        for y in range(0, self.data.height(), PixelData.asset_height):
            for x in range(0, self.data.width(), PixelData.asset_width):
                tile_data = []

                # Extract pixel data for the current tile
                for row in range(PixelData.asset_height):
                    row_data = []
                    for col in range(PixelData.asset_width):
                        # Append the RGB color tuple to the row data
                        row_data.append(self.data.pixelIndex(x + col, y + row))
                    # Append the row data to the tile data
                    tile_data.append(row_data)

                # Create a JSON representation of the tile and add it to the list
                asset = {
                    "name": self.names[name_index],
                    "contents": tile_data
                }
                image_data.append(asset)
                name_index += 1

        return image_data


def history_add_pixel_palette_row(undo_stack, pixel_data):
    undo_stack.push(
        cmdAddPixelRow(
            pixel_data,
            "Add palette row"
        )
    )

def history_remove_pixel_palette_row(undo_stack, pixel_data):
    if pixel_data.get_image().height() - 8 <= 0:
        pixel_data.error_thrown.emit("At least one row of assets is required")
        return

    undo_stack.push(
        cmdRemovePixelRow(
            pixel_data,
            "Remove palette row"
        )
    )

def history_set_asset_name(undo_stack, pixel_data, asset_index, new_asset_name):
    if not new_asset_name:
        pixel_data.error_thrown.emit("Name cannot be blank")
        return
    if new_asset_name in pixel_data.get_names():
        pixel_data.error_thrown.emit("An asset with this name already exists")
        return

    undo_stack.push(
        cmdSetAssetName(
            pixel_data,
            asset_index,
            new_asset_name,
            "Rename asset"
        )
    )

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
