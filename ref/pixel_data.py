from collections import OrderedDict, namedtuple
import json
from math import ceil, floor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor, QImage
# from colorpicker import upsample
from PyQt5.QtWidgets import QUndoStack, QMessageBox
from history import(
    cmdAddPixelRow,
    cmdRemovePixelRow
)

class PixelData(QObject):

    data_updated = pyqtSignal()
    error_thrown = pyqtSignal(str)

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

    def set_names(self, names):
        self.names = names

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

def history_add_pixel_palette_row(undo_stack, pixel_data):
    undo_stack.push(
        cmdAddPixelRow(
            pixel_data,
            "Add palette row"
        )
    )

def history_remove_pixel_palette_row(undo_stack, pixel_data):
    if pixel_data.get_image().height() - 8 <= 0:
        pixel_data.error_thrown.emit("At least one row of elements is required")
        return

    undo_stack.push(
        cmdRemovePixelRow(
            pixel_data,
            "Remove palette row"
        )
    )

def parse_pixel_data(data):
    pixels_per_element = 64
    element_width = 8
    element_height = 8
    elements_per_line = 16
    pixel_data = bytearray([0] * len(data) * pixels_per_element)
    names = []

    for index, palette in enumerate(data):
        names.append(palette["name"])
        col_index = floor(index / elements_per_line) * element_width * elements_per_line * element_height
        col_offset = (index % elements_per_line) * element_width
        for pixel_row, pixel_row_data in enumerate(palette["contents"]):
            row_offset = pixel_row * elements_per_line * element_width
            pixel_data_index = col_index + row_offset + col_offset
            pixel_data[pixel_data_index:pixel_data_index+8] = pixel_row_data

    width = element_width * elements_per_line
    height = ceil(len(pixel_data) / width)
    return (pixel_data, width, height, names)
