from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from history import *
from sources import Sources
from colorpalette import upsample
import json
import math
from collections import OrderedDict

class ColorPalettes(QObject):
    color_changed = pyqtSignal(str)
    name_changed = pyqtSignal(str, str)
    palette_added = pyqtSignal(str, int)
    palette_removed = pyqtSignal(str)

    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.palettes = OrderedDict()
        for spr_pal in data:
            palette = spr_pal["contents"]
            palette[:] = [QColor(*upsample(color>>5, (color>>2)&7, color&3)) for color in palette]
            if source is Sources.SPRITE:
                palette[0] = QColor(0,0,0,0)
            self.palettes[spr_pal["name"]] = palette

    def keys(self):
        return self.palettes.keys()

    def values(self):
        return self.palettes.values()

    def items(self):
        return self.palettes.items()

    def setName(self, cur_name, new_name):
        replacement = {cur_name: new_name}
        temp_palette_items = self.palettes.copy()
        for name, _ in self.palettes.items():
            temp_palette_items[replacement.get(name, name)] = temp_palette_items.pop(name)
        self.palettes = temp_palette_items
        self.name_changed.emit(cur_name, new_name)

    def addPalette(self, name, contents, index=None):
        contents[0] = QColor(0,0,0,0)
        new_palettes = OrderedDict()
        cur_palette = 0
        if index == None or index == len(self.palettes):
            index = len(self.palettes)
            self.palettes[name] = contents
        else:
            for key, value in self.palettes.items():
                if cur_palette == index:
                    new_palettes[name] = contents
                new_palettes[key] = value
                cur_palette += 1
            self.palettes = new_palettes
        self.palette_added.emit(name, index)

    def remPalette(self, name):
        if name in self.palettes:
            del self.palettes[name]
            self.palette_removed.emit(name)
        else:
            self.palette_removed.emit(None)

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
    batch_updated = pyqtSignal(set)
    row_count_updated = pyqtSignal(int)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.update_manifest = set()
        self.palettes = []
        for sprite in data:
            self.palettes.append(sprite["contents"])

    def batchUpdate(self):
        self.batch_updated.emit(self.update_manifest)
        self.update_manifest.clear()

    def getPalettes(self):
        return self.palettes

    def addRow(self, row):
        self.palettes.extend(row)
        self.row_count_updated.emit(math.floor(self.palettes.__len__()/16))

    def remRow(self):
        old_row = self.palettes[-16:]
        del self.palettes[-16:]
        self.row_count_updated.emit(math.floor(self.palettes.__len__()/16))
        return old_row

    def __getitem__(self, index):
        return self.palettes[index]

    def __setitem__(self, index, value):
        index, row, col = index
        self.palettes[index][row][col] = value
        self.update_manifest.add(index)

class GameData(QObject):
    spr_col_pal_updated = pyqtSignal(str)
    spr_col_pal_renamed = pyqtSignal(str, str)
    spr_col_pal_added = pyqtSignal(str, int)
    spr_col_pal_removed = pyqtSignal(str)
    spr_batch_updated = pyqtSignal(set)
    spr_row_count_updated = pyqtSignal(int)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.undo_stack = QUndoStack(self)

        self.sprite_pixel_palettes = PixelPalettes(data["sprites"])
        self.sprite_color_palettes = ColorPalettes(data["spriteColorPalettes"], Sources.SPRITE)
        self.sprite_pixel_palettes.batch_updated.connect(self.spr_batch_updated)
        self.sprite_color_palettes.color_changed.connect(self.spr_col_pal_updated)
        self.sprite_pixel_palettes.row_count_updated.connect(self.spr_row_count_updated)
        self.sprite_color_palettes.name_changed.connect(self.spr_col_pal_renamed)
        self.sprite_color_palettes.palette_added.connect(self.spr_col_pal_added)
        self.sprite_color_palettes.palette_removed.connect(self.spr_col_pal_removed)

    def getSprites(self):
        return self.sprite_pixel_palettes.getPalettes()

    def getSprite(self, index):
        return self.sprite_pixel_palettes[index]

    def getSprColPals(self):
        return self.sprite_color_palettes.values()

    def getSprColPal(self, name):
        return self.sprite_color_palettes[name]

    def setSprCol(self, name, index, color, orig=None):
        command = cmdSetSprCol(self.sprite_color_palettes, name, index, color, orig, "Set palette color")
        self.undo_stack.push(command)

    def previewSprCol(self, name, index, color):
        self.sprite_color_palettes[name, index] = color

    def setSprColPalName(self, cur_name, new_name):
        if new_name not in self.sprite_color_palettes.keys():
            command = cmdSetSprColPalName(self.sprite_color_palettes, cur_name, new_name, "Set palette name")
            self.undo_stack.push(command)
        else:
            self.spr_col_pal_renamed.emit(None, None)

    def addSprColPal(self, name):
        if name not in self.sprite_color_palettes.keys():
            command = cmdAddSprColPal(self.sprite_color_palettes, name, [QColor(0,0,0,255)]*16, "Add color palette")
            self.undo_stack.push(command)
        else:
            self.spr_col_pal_added.emit(None, None)

    def remSprColPal(self, name):
        if name in self.sprite_color_palettes.keys():
            command = cmdRemSprColPal(self.sprite_color_palettes, name, "Add color palette")
            self.undo_stack.push(command)
        else:
            self.spr_col_pal_removed.emit(None)

    def setSprPixBatch(self, batch):
        command = cmdSetSprPixBatch(self.sprite_pixel_palettes, batch, "Draw pixels")
        self.undo_stack.push(command)

    def addSprPixRow(self):
        command = cmdAddSprPixRow(self.sprite_pixel_palettes, "Add Sprite Row")
        self.undo_stack.push(command)

    def remSprPixRow(self):
        command = cmdRemSprPixRow(self.sprite_pixel_palettes, "Remove Sprite Row")
        self.undo_stack.push(command)

    def setUndoStack(self, undo_stack):
        self.undo_stack = undo_stack

    @classmethod
    def fromFilename(cls, file_name, parent=None):
        with open(file_name, 'r') as data_file:
                return cls(json.load(data_file), parent)
