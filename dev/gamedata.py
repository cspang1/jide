from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from colorpalette import upsample
import json

class ColorPalette(QObject):
    data_changed = pyqtSignal(int)

    def __init__(self, data):
        QObject.__init__(self)
        self.name = data["name"]
        self.colors = []
        for color in data["contents"]:
            self.colors.append(qRgb(*upsample(color>>5, (color>>2)&7, color&3)))

    def __getitem__(self, index):
        return self.colors[index]

    def __setitem__(self, index, value):
        self.colors[index] = value
        self.data_changed.emit(index)

class PixelPalette(QObject):
    data_changed = pyqtSignal(int, int)

    def __init__(self, data):
        QObject.__init__(self)
        self.name = data["name"]
        self.pixels = data["contents"]

    def __getitem__(self, index):
        row, col = index
        return self.pixels[row][col]

    def __setitem__(self, index, value):
        row, col = index
        self.pixels[row][col] = value
        self.data_changed.emit(row, col)

class GameData():
    data_changed = pyqtSignal(int, int)

    def __init__(self, data):
        self.sprite_color_palettes = []
        for spr_pal in data["spriteColorPalettes"]:
            self.sprite_color_palettes.append(ColorPalette(spr_pal))
        self.tile_color_palettes = []
        for tile_pal in data["tileColorPalettes"]:
            self.tile_color_palettes.append(ColorPalette(tile_pal))
        self.sprite_pixel_palettes = []
        for sprite in data["sprites"]:
            self.sprite_pixel_palettes.append(PixelPalette(sprite))
        self.tile_pixel_palettes = []
        for tile in data["tiles"]:
            self.tile_pixel_palettes.append(PixelPalette(tile))
        self.tile_maps= data["tileMaps"]

    @classmethod
    def from_filename(cls, file_name):
        with open(file_name, 'r') as data_file:
                return cls(json.load(data_file))

