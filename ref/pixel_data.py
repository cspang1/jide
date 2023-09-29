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

    def __init__(self, data, width, height, names):
        super().__init__(data, width, height, QImage.Format_Indexed8)
        self.names = names
