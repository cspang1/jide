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


class ColorData(QObject):

    color_palette_added = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_data = OrderedDict()

    def add_color_palette(self, color_palette_name, color_palette_data):
        self.color_data[color_palette_name] = color_palette_data
        self.color_palette_added.emit(color_palette_name)

    def get_color_palette(self, color_palette_name):
        return self.color_data[color_palette_name]

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
