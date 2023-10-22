from collections import OrderedDict
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QColor
from history import(
    cmdSetCol,
    cmdRenameColPal,
    cmdAddColPal,
    cmdRemoveColPal
)

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
                r, g, b = downsample(color.red(), color.green(), color.blue())
                color = (r << 5) | (g << 2) | b
                colors.append(color)

            palette = {
                "name": color_palette_name,
                "contents": colors
            }
            
            color_data.append(palette)

        return color_data

def history_set_color(undo_stack, color_data, palette_name, new_color, change_index):
    undo_stack.push(
        cmdSetCol(
            color_data,
            palette_name,
            new_color,
            change_index,
            "Set palette color"
        )
    )

def history_rename_color_palette(undo_stack, color_data, old_palette_name, new_palette_name):
    if new_palette_name in color_data.get_color_data() and old_palette_name != new_palette_name:
        color_data.error_thrown.emit("A color palette with that name already exists")
        return
    if old_palette_name == new_palette_name:
        return

    undo_stack.push(
        cmdRenameColPal(
            color_data,
            old_palette_name,
            new_palette_name,
            "Rename color palette"
        )
    )

def history_add_color_palette(undo_stack, color_data, palette_name):
    if palette_name in color_data.get_color_data():
        color_data.error_thrown.emit("A color palette with that name already exists")
        return

    undo_stack.push(
        cmdAddColPal(
            color_data,
            palette_name,
            [QColor(255, 0, 255)] * 16,
            "Add  color palette"
        )
    )

def history_remove_color_palette(undo_stack, color_data, palette_name):
    if len(color_data.get_color_data()) == 1:
        color_data.error_thrown.emit("At least one color palette is required")
        return

    undo_stack.push(
        cmdRemoveColPal(
            color_data,
            palette_name,
            "Remove color palette"
        )
    )

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
