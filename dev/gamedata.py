from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from undosys import *
from colorpalette import upsample
import json
from palettize import palettize

class ColorPalettes(QObject):
    color_changed = pyqtSignal(str)

    def __init__(self, data):
        super().__init__()
        self.palettes = {}
        for spr_pal in data:
            palette = spr_pal["contents"]
            palette[:] = [QColor(*upsample(color>>5, (color>>2)&7, color&3)) for color in palette]
            palette[0] = QColor(0,0,0,0)
            self.palettes[spr_pal["name"]] = palette

    def values(self):
        return self.palettes.values()

    def items(self):
        return self.palettes.items()

    def __getitem__(self, index):
        if not isinstance(index, tuple):
            return self.palettes[index]
        name, index = index
        return self.palettes[name][index]

    def __setitem__(self, index, value):
        name, index = index
        self.palettes[name][index] = value
        self.color_changed.emit(name)

class PixelPalettes(QObject):
    pixel_changed = pyqtSignal(int, int)

    def __init__(self, data):
        super().__init__()
        self.palettes = {}
        for sprite in data:
            self.palettes[sprite["name"]] = sprite["contents"]

    def values(self):
        return self.palettes.values()

    def items(self):
        return self.palettes.items()

    def __getitem__(self, index):
        if not isinstance(index, tuple):
            return self.palettes[index]
        name, row, col = index
        return self.palettes[name][row][col]

    def __setitem__(self, index, value):
        name, row, col = index
        self.palettes[name][row][col] = value
        self.pixel_changed.emit(row, col)

class GameData(QObject):
    spr_col_updated = pyqtSignal(str)
    spr_pix_updated = pyqtSignal(int, int)
    tile_col_updated = pyqtSignal(str)
    tile_pix_updated = pyqtSignal(int, int)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.undo_stack = QUndoStack(self)

        self.sprite_pixel_palettes = PixelPalettes(data["sprites"])
        self.tile_pixel_palettes = PixelPalettes(data["tiles"])
        self.sprite_color_palettes = ColorPalettes(data["spriteColorPalettes"])
        self.tile_color_palettes = ColorPalettes(data["tileColorPalettes"])
        self.sprite_pixel_palettes.pixel_changed.connect(self.spr_pix_updated)
        self.tile_pixel_palettes.pixel_changed.connect(self.tile_pix_updated)
        self.sprite_color_palettes.color_changed.connect(self.spr_col_updated)
        self.tile_color_palettes.color_changed.connect(self.tile_col_updated)

    def getSprite(self, name):
        return self.sprite_pixel_palettes[name]

    def getTile(self, name):
        return self.tile_pixel_palettes[name]

    def getSprColPal(self, name):
        return self.sprite_color_palettes[name]

    def getTileColPal(self, name):
        return self.tile_color_palettes[name]

    def getTileMap(self, name):
        return self.tile_maps[name]

    def setSprCol(self, name, index, color, orig=None):
        command = cmdSetSprCol(self.sprite_color_palettes, name, index, color, orig, "Set palette color")
        self.undo_stack.push(command)

    def setSprPix(self, name, row, col, value):
        command = cmdSetSprPix(self.sprite_pixel_palettes, name, row, col, value, "Draw pixel")
        self.undo_stack.push(command)

    def setUndoStack(self, undo_stack):
        self.undo_stack = undo_stack

    def previewSprCol(self, name, index, color):
        self.sprite_color_palettes[name, index] = color

    @classmethod
    def fromFilename(cls, file_name, parent=None):
        with open(file_name, 'r') as data_file:
                return cls(json.load(data_file), parent)
