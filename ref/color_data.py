from collections import OrderedDict
import json
from math import ceil, floor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QSize
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

class ColorData(QObject):

    color_palette_added = pyqtSignal(str)
    color_palette_removed = pyqtSignal(str)
    color_palette_renamed = pyqtSignal(str, str)
    color_updated = pyqtSignal(str, QColor, int)
    error_thrown = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_data = OrderedDict()

    @pyqtSlot(str, list)
    def add_color_palette(self, color_palette_name, color_palette_data):
        if color_palette_name in self.color_data:
            self.error_thrown.emit("A color palette with that name already exists")
            return
        self.color_data[color_palette_name] = color_palette_data
        self.color_palette_added.emit(color_palette_name)

    @pyqtSlot(str)
    def remove_color_palette(self, color_palette_name):
        if len(self.color_data) == 1:
            self.error_thrown.emit("At least one color palette is required")
            return
        del self.color_data[color_palette_name]
        self.color_palette_removed.emit(color_palette_name)

    @pyqtSlot(str, str)
    def rename_color_palette(self, old_color_palette_name, new_color_palette_name):
        if new_color_palette_name in self.color_data and old_color_palette_name != new_color_palette_name:
            self.error_thrown.emit("A color palette with that name already exists")
            return
        color_palette_data = self.color_data[old_color_palette_name]
        del self.color_data[old_color_palette_name]
        self.color_data[new_color_palette_name] = color_palette_data
        self.color_palette_renamed.emit(old_color_palette_name, new_color_palette_name)

    @pyqtSlot(str)
    def get_color_palette(self, color_palette_name):
        return self.color_data[color_palette_name]

    @pyqtSlot(str, QColor, int)
    def update_color(self, color_palette_name, color, index):
        self.color_data[color_palette_name][index] = color
        self.color_updated.emit(color_palette_name, color, index)


def upsample(red, green, blue):
    """Upsamples RGB from 8-bit to 24-bit

    :param red:     8-bit red value
    :type red:      int
    :param green:   8-bit green value
    :type green:    int
    :param blue:    8-bit blue value
    :type blue:     int
    :return:        24-bit upscaled RGB tuple
    :rtype:         tuple(int, int, int)
    """
    red = round((red / 7) * 255)
    green = round((green / 7) * 255)
    blue = round((blue / 3) * 255)
    return (red, green, blue)

def downsample(red, green, blue):
    """Downsamples RGB from 24-bit to 8-bit

    :param red:     24-bit red value
    :type red:      int
    :param green:   24-bit green value
    :type green:    int
    :param blue:    24-bit blue value
    :type blue:     int
    :return:        8-bit downscaled RGB tuple
    :rtype:         tuple(int, int, int)
    """
    red = round((red / 255) * 7)
    green = round((green / 255) * 7)
    blue = round((blue / 255) * 3)
    return (red, green, blue)

def normalize(red, green, blue):
    """Normalizes any RGB value to be representable by a whole 8-bit value

    :param red:     Red value
    :type red:      int
    :param green:   Green value
    :type green:    int
    :param blue:    Blue value
    :type blue:     int
    :return:        24-bit normalized RGB tuple
    :rtype:         tuple(int, int, int)
    """
    return upsample(*downsample(red, green, blue))

def parse_color_data(data):
    for palette in data:
        cur_pal = palette["contents"]
        cur_pal[:] = [
            QColor(*upsample(color >> 5, (color >> 2) & 7, color & 3))
            for color in cur_pal
        ]
        yield (palette["name"], cur_pal)
