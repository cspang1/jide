from collections import OrderedDict
import json
import math
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from colorpicker import upsample
from PyQt5.QtWidgets import QUndoStack
from history import cmdAddColPal, cmdAddPixRow, cmdRemColPal, cmdRemPixRow, cmdSetCol, cmdSetColPalName, cmdSetPixBatch
from source import Source

class ColorPalettes(QObject):
    color_changed = pyqtSignal(Source, str)
    name_changed = pyqtSignal(Source, str, str)
    palette_added = pyqtSignal(Source, str, int)
    palette_removed = pyqtSignal(Source, str)

    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.palettes = OrderedDict()
        self.source = source
        for spr_pal in data:
            palette = spr_pal["contents"]
            palette[:] = [QColor(*upsample(color>>5, (color>>2)&7, color&3)) for color in palette]
            if self.source is Source.SPRITE:
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
        self.name_changed.emit(self.source, cur_name, new_name)

    def addPalette(self, name, contents, index=None):
        if self.source is Source.SPRITE:
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
        self.palette_added.emit(self.source, name, index)

    def remPalette(self, name):
        if name in self.palettes:
            del self.palettes[name]
            self.palette_removed.emit(self.source, name)
        else:
            self.palette_removed.emit(self.source, None)

    def __getitem__(self, index):
        if not isinstance(index, tuple):
            return self.palettes[index]
        name, index = index
        return self.palettes[name][index]

    def __setitem__(self, index, value):
        name, index = index
        self.palettes[name][index] = value
        self.color_changed.emit(self.source, name)

class PixelPalettes(QObject):
    batch_updated = pyqtSignal(Source, set)
    row_count_updated = pyqtSignal(Source, int)

    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.update_manifest = set()
        self.palettes = []
        self.source = source
        for element in data:
            self.palettes.append(element["contents"])

    def batchUpdate(self):
        self.batch_updated.emit(self.source, self.update_manifest)
        self.update_manifest.clear()

    def getPalettes(self):
        return self.palettes

    def addRow(self, row=None):
        self.palettes.extend([[[0]*8 for i in range(8)]for i in range(16)] if row is None else row)
        self.row_count_updated.emit(self.source, math.floor(self.palettes.__len__()/16))

    def remRow(self):
        old_row = self.palettes[-16:]
        del self.palettes[-16:]
        self.row_count_updated.emit(self.source, math.floor(self.palettes.__len__()/16))
        return old_row

    def __getitem__(self, index):
        return self.palettes[index]

    def __setitem__(self, index, value):
        index, row, col = index
        self.palettes[index][row][col] = value
        self.update_manifest.add(index)

class GameData(QObject):
    col_pal_updated = pyqtSignal(Source, str)
    col_pal_renamed = pyqtSignal(Source, str, str)
    col_pal_added = pyqtSignal(Source, str, int)
    col_pal_removed = pyqtSignal(Source, str)
    pix_batch_updated = pyqtSignal(Source, set)
    row_count_updated = pyqtSignal(Source, int)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.undo_stack = QUndoStack(self)

        self.sprite_pixel_palettes = PixelPalettes(data["sprites"], Source.SPRITE)
        self.tile_pixel_palettes = PixelPalettes(data["tiles"], Source.TILE)
        self.sprite_color_palettes = ColorPalettes(data["spriteColorPalettes"], Source.SPRITE)
        self.tile_color_palettes = ColorPalettes(data["tileColorPalettes"], Source.TILE)
        self.sprite_pixel_palettes.batch_updated.connect(self.pix_batch_updated)
        self.tile_pixel_palettes.batch_updated.connect(self.pix_batch_updated)
        self.sprite_color_palettes.color_changed.connect(self.col_pal_updated)
        self.tile_color_palettes.color_changed.connect(self.col_pal_updated)
        self.sprite_pixel_palettes.row_count_updated.connect(self.row_count_updated)
        self.tile_pixel_palettes.row_count_updated.connect(self.row_count_updated)
        self.sprite_color_palettes.name_changed.connect(self.col_pal_renamed)
        self.tile_color_palettes.name_changed.connect(self.col_pal_renamed)
        self.sprite_color_palettes.palette_added.connect(self.col_pal_added)
        self.tile_color_palettes.palette_added.connect(self.col_pal_added)
        self.sprite_color_palettes.palette_removed.connect(self.col_pal_removed)
        self.tile_color_palettes.palette_removed.connect(self.col_pal_removed)

    def getPixelPalettes(self, source):
        return self.sprite_pixel_palettes.getPalettes() if source is Source.SPRITE else self.tile_pixel_palettes.getPalettes()

    def getElement(self, index, source):
        return self.sprite_pixel_palettes[index] if source is Source.SPRITE else self.tile_pixel_palettes[index]

    def getColPals(self, source):
        return self.sprite_color_palettes.values() if source is Source.SPRITE else self.tile_color_palettes.values()

    def getColPalNames(self, source):
        return self.sprite_color_palettes.keys() if source is Source.SPRITE else self.tile_color_palettes.keys()

    def getColPal(self, name, source):
        return self.sprite_color_palettes[name] if source is Source.SPRITE else self.tile_color_palettes[name]

    def setColor(self, name, index, color, source, orig=None):
        target = self.sprite_color_palettes if source is Source.SPRITE else self.tile_color_palettes
        command = cmdSetCol(target, name, index, color, orig, "Set palette color")
        self.undo_stack.push(command)

    def previewColor(self, name, index, color, source):
        if source is Source.SPRITE:
            self.sprite_color_palettes[name, index] = color
        else:
            self.tile_color_palettes[name, index] = color

    def setColPalName(self, cur_name, new_name, source):
        if source is Source.SPRITE:
            if new_name not in self.sprite_color_palettes.keys():
                command = cmdSetColPalName(self.sprite_color_palettes, cur_name, new_name, "Set palette name")
                self.undo_stack.push(command)
            else:
                self.col_pal_renamed.emit(source, None, None)
        else:
            if new_name not in self.tile_color_palettes.keys():
                command = cmdSetColPalName(self.tile_color_palettes, cur_name, new_name, "Set palette name")
                self.undo_stack.push(command)
            else:
                self.col_pal_renamed.emit(source, None, None)

    def addColPal(self, name, source):
        if source is Source.SPRITE:
            if name not in self.sprite_color_palettes.keys():
                command = cmdAddColPal(self.sprite_color_palettes, name, [QColor(0,0,0,255)]*16, "Add color palette")
                self.undo_stack.push(command)
            else:
                self.col_pal_added.emit(source, None, None)
        else:
            if name not in self.tile_color_palettes.keys():
                command = cmdAddColPal(self.tile_color_palettes, name, [QColor(0,0,0,255)]*16, "Add color palette")
                self.undo_stack.push(command)
            else:
                self.col_pal_added.emit(source, None, None)

    def remColPal(self, name, source):
        if source is Source.SPRITE:
            if name in self.sprite_color_palettes.keys():
                command = cmdRemColPal(self.sprite_color_palettes, name, "Add color palette")
                self.undo_stack.push(command)
            else:
                self.col_pal_removed.emit(source, None)
        else:
            if name in self.tile_color_palettes.keys():
                command = cmdRemColPal(self.tile_color_palettes, name, "Add color palette")
                self.undo_stack.push(command)
            else:
                self.col_pal_removed.emit(source, None)

    def setPixBatch(self, batch, source):
        target = self.sprite_pixel_palettes if source is Source.SPRITE else self.tile_pixel_palettes
        command = cmdSetPixBatch(target, batch, "Draw pixels")
        self.undo_stack.push(command)

    def addPixRow(self, source):
        target = self.sprite_pixel_palettes if source is Source.SPRITE else self.tile_pixel_palettes
        target_name = "sprite" if source is Source.SPRITE else "tile"
        command = cmdAddPixRow(target, "Add {} row".format(target_name))
        self.undo_stack.push(command)

    def remPixRow(self, source):
        target = self.sprite_pixel_palettes if source is Source.SPRITE else self.tile_pixel_palettes
        target_name = "sprite" if source is Source.SPRITE else "tile"
        command = cmdRemPixRow(target, "Add {} row".format(target_name))
        self.undo_stack.push(command)

    def setUndoStack(self, undo_stack):
        self.undo_stack = undo_stack

    @classmethod
    def fromFilename(cls, file_name, parent=None):
        with open(file_name, 'r') as data_file:
                return cls(json.load(data_file), parent)
