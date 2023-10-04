from collections import OrderedDict
import json
from math import ceil, floor
from PyQt5.QtCore import QObject, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QImage
# from colorpicker import upsample
from PyQt5.QtWidgets import QUndoStack, QMessageBox
# from history import (
#     cmdAddColPal,
#     cmdAddPixRow,
#     cmdRemColPal,
#     cmdRemPixRow,
#     cmdSetCol,
#     cmdSetColPalName,
#     cmdSetPixBatch,
# )

class PixelData(QImage):

    def __init__(self, data, width, height, names):
        super().__init__(data, width, height, QImage.Format_Indexed8)
        self.names = names

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
