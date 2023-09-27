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
from source import Source


class PixelData(QImage):

    def __init__(self, jrf_data):
        pixels_per_sprite = 64
        sprite_width = 8
        sprites_per_line = 16
        pixel_data = bytearray([0] * len(jrf_data) * pixels_per_sprite)
        names = []

        try:
            for index, element in enumerate(jrf_data):
                names.append(element["name"])
                for pixel_col, pixel_row_data in enumerate(element["contents"]):
                    pixel_data_index = \
                        pixel_col * sprites_per_line * sprite_width + \
                        (index % sprites_per_line) * sprite_width + \
                        floor(index / sprites_per_line) * sprite_width
                    pixel_data[pixel_data_index:8] = pixel_row_data
        except KeyError:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to load project due to malformed data",
            ).exec()
            return

        width = sprite_width * sprites_per_line
        height = ceil(len(pixel_data) / sprites_per_line) * sprite_width
        super().__init__(pixel_data, width, height, QImage.Format_Indexed8)
