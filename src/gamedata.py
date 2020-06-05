from collections import OrderedDict
import json
import math
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from .colorpicker import upsample
from PyQt5.QtWidgets import QUndoStack
from .history import (
    cmdAddColPal,
    cmdAddPixRow,
    cmdRemColPal,
    cmdRemPixRow,
    cmdSetCol,
    cmdSetColPalName,
    cmdSetPixBatch,
)
from .source import Source


class ColorPalettes(QObject):
    """Data container for sprite/tile color palettes

    :param data: List containing JSON color palette data
    :type data: list(dict)
    :param source: Subject source of palette, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

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
            palette[:] = [
                QColor(*upsample(color >> 5, (color >> 2) & 7, color & 3))
                for color in palette
            ]
            if self.source is Source.SPRITE:
                palette[0] = QColor(0, 0, 0, 0)
            self.palettes[spr_pal["name"]] = palette

    def keys(self):
        """Retrieve color palette dict keys

        :return: Color palette dict keys
        :rtype: odict_keys
        """
        return self.palettes.keys()

    def values(self):
        """Retrieve color palette dict values

        :return: Color palette dict values
        :rtype: odict_values
        """
        return self.palettes.values()

    def items(self):
        """Retrieve color palette dict items

        :return: Color palette dict items
        :rtype: odict_items
        """
        return self.palettes.items()

    def setName(self, cur_name, new_name):
        """Sets the names of a color palette

        :param cur_name: Name of target color palette
        :type cur_name: str
        :param new_name: New name for color palette
        :type new_name: str
        """
        replacement = {cur_name: new_name}
        temp_palette_items = self.palettes.copy()
        for name, _ in self.palettes.items():
            temp_palette_items[replacement.get(name, name)] = temp_palette_items.pop(
                name
            )
        self.palettes = temp_palette_items
        self.name_changed.emit(self.source, cur_name, new_name)

    def addPalette(self, name, contents, index=None):
        """Add a new color palette

        :param name: New color palette name
        :type name: str
        :param contents: New color palette contents
        :type contents: list(QColor)
        :param index: Index in palettes to insert new palette, defaults to None
        :type index: int, optional
        """
        if self.source is Source.SPRITE:
            contents[0] = QColor(0, 0, 0, 0)
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
        """Removes color palette

        :param name: Name of color palette to be removed
        :type name: str
        """
        if name in self.palettes:
            del self.palettes[name]
            self.palette_removed.emit(self.source, name)
        else:
            self.palette_removed.emit(self.source, None)

    def __getitem__(self, index):
        """Retrieves a color palette or color at a given index

        :param index: Index of color palette or color
        :type index: int OR tuple(str, int)
        :return: Color palette OR color
        :rtype: list(QColor) OR QColor
        """
        if not isinstance(index, tuple):
            return self.palettes[index]
        name, index = index
        return self.palettes[name][index]

    def __setitem__(self, index, value):
        """Set color in palette

        :param index: Index of color to be set
        :type index: tuple(str, int)
        :param value: New color value
        :type value: QColor
        """
        name, index = index
        self.palettes[name][index] = value
        self.color_changed.emit(self.source, name)


class PixelPalettes(QObject):
    """Data container for sprite/tile pixel palettes

    :param data: List containing JSON pixel palette data
    :type data: list(dict)
    :param source: Subject source of palette, either sprite or tile
    :type source: Source
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

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
        """Updates the pixel palette date based on self.update_manifest
        """
        self.batch_updated.emit(self.source, self.update_manifest)
        self.update_manifest.clear()

    def getPalettes(self):
        """Returns the pixel palettes

        :return: Pixel palettes
        :rtype: list(list)
        """
        return self.palettes

    def addRow(self, row=None):
        """Adds a row of sprites/tiles to palette

        :param row: Row data to be added, defaults to None
        :type row: list(list), optional
        """
        self.palettes.extend(
            [[[0] * 8 for i in range(8)] for i in range(16)] if row is None else row
        )
        self.row_count_updated.emit(
            self.source, math.floor(self.palettes.__len__() / 16)
        )

    def remRow(self):
        """Removes a row of sprites/tiles from the palette

        :return: The removed row
        :rtype: list(list)
        """
        old_row = self.palettes[-16:]
        del self.palettes[-16:]
        self.row_count_updated.emit(
            self.source, math.floor(self.palettes.__len__() / 16)
        )
        return old_row

    def __getitem__(self, index):
        """Retrieves a pixel palette at an index

        :param index: Index of pixel palette
        :type index: int
        :return: Pixel palette at index
        :rtype: list(list)
        """
        return self.palettes[index]

    def __setitem__(self, index, value):
        """Sets pixel at index to a value

        :param index: Sprite/tile index/row/column
        :type index: tuple(int, int, int)
        :param value: Value to set pixel to
        :type value: int
        """
        index, row, col = index
        self.palettes[index][row][col] = value
        self.update_manifest.add(index)


class GameData(QObject):
    """Represents centralized data object for JIDE, containing all sprite/tile/tile map data and CRUD functions

    :param data: Dict containing project JSON data
    :type data: dict
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

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
        self.sprite_color_palettes = ColorPalettes(
            data["spriteColorPalettes"], Source.SPRITE
        )
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
        """Retrieve sprite/tile pixel palettes

        :param source: Subject source of palettes, either sprite or tile
        :type source: Source
        :return: Pixel palettes
        :rtype: list
        """
        return (
            self.sprite_pixel_palettes.getPalettes()
            if source is Source.SPRITE
            else self.tile_pixel_palettes.getPalettes()
        )

    def getElement(self, index, source):
        """Retrieve a sprite/tile pixel value

        :param index: Index/row/col of pixel
        :type index: tuple(int, int, int)
        :param source: Subject source of pixel, either sprite or tile
        :type source: Source
        :return: Pixel value at index
        :rtype: int
        """
        return (
            self.sprite_pixel_palettes[index]
            if source is Source.SPRITE
            else self.tile_pixel_palettes[index]
        )

    def getColPals(self, source):
        """Retrieve sprite/tile color palettes

        :param source: Subject source of palettes, either sprite or tile
        :type source: Source
        :return: Color palettes of target source
        :rtype: list
        """
        return (
            self.sprite_color_palettes.values()
            if source is Source.SPRITE
            else self.tile_color_palettes.values()
        )

    def getColPalNames(self, source):
        """Retrieve sprite/tile color palette names

        :param source: Subject source of palette names, either sprite or tile
        :type source: Source
        :return: Names of target source color palettes
        :rtype: list
        """
        return (
            self.sprite_color_palettes.keys()
            if source is Source.SPRITE
            else self.tile_color_palettes.keys()
        )

    def getColPal(self, name, source):
        """Retrieve a specific sprite/tile color palette

        :param name: Name of color palette to retrieve
        :type name: str
        :param source: Subject source of palette, either sprite or tile
        :type source: Source
        :return: Color palette specified by name
        :rtype: list
        """
        return (
            self.sprite_color_palettes[name]
            if source is Source.SPRITE
            else self.tile_color_palettes[name]
        )

    def setColor(self, name, index, color, source, orig=None):
        """Sets a color in a specific color palette

        :param name: Name of color palette containing target color
        :type name: str
        :param index: Index of color in color palette
        :type index: int
        :param color: New color to be set to
        :type color: QColor
        :param source: Subject source of target palette, either sprite or tile
        :type source: Source
        :param orig: Original color of the target color, defaults to None
        :type orig: QColor, optional
        """
        target = (
            self.sprite_color_palettes
            if source is Source.SPRITE
            else self.tile_color_palettes
        )
        command = cmdSetCol(target, name, index, color, orig, "Set palette color")
        self.undo_stack.push(command)

    def previewColor(self, name, index, color, source):
        """Previews a color without committing it to the data; used by colorpalette.ColorPreview

        :param name: Name of color palette containing target color
        :type name: str
        :param index: Index of color in color palette
        :type index: int
        :param color: Color to preview
        :type color: QColor
        :param source: Subject source of target palette, either sprite or tile
        :type source: Source
        """
        if source is Source.SPRITE:
            self.sprite_color_palettes[name, index] = color
        else:
            self.tile_color_palettes[name, index] = color

    def setColPalName(self, cur_name, new_name, source):
        """Set name of a color palette

        :param cur_name: Current name of target color palette
        :type cur_name: str
        :param new_name: New name for target palette
        :type new_name: str
        :param source: Subject source of target palette, either sprite or tile
        :type source: Source
        """
        if source is Source.SPRITE:
            if new_name not in self.sprite_color_palettes.keys():
                command = cmdSetColPalName(
                    self.sprite_color_palettes, cur_name, new_name, "Set palette name"
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_renamed.emit(source, None, None)
        else:
            if new_name not in self.tile_color_palettes.keys():
                command = cmdSetColPalName(
                    self.tile_color_palettes, cur_name, new_name, "Set palette name"
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_renamed.emit(source, None, None)

    def addColPal(self, name, source):
        """Add a new color palette

        :param name: Name for the new color palette
        :type name: str
        :param source: Subject source of new palette, either sprite or tile
        :type source: Source
        """
        if source is Source.SPRITE:
            if name not in self.sprite_color_palettes.keys():
                command = cmdAddColPal(
                    self.sprite_color_palettes,
                    name,
                    [QColor(0, 0, 0, 255)] * 16,
                    "Add color palette",
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_added.emit(source, None, None)
        else:
            if name not in self.tile_color_palettes.keys():
                command = cmdAddColPal(
                    self.tile_color_palettes,
                    name,
                    [QColor(0, 0, 0, 255)] * 16,
                    "Add color palette",
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_added.emit(source, None, None)

    def remColPal(self, name, source):
        """Remove a color palette

        :param name: Name for the target color palette
        :type name: str
        :param source: Subject source of target palette, either sprite or tile
        :type source: Source
        """
        if source is Source.SPRITE:
            if name in self.sprite_color_palettes.keys():
                command = cmdRemColPal(
                    self.sprite_color_palettes, name, "Add color palette"
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_removed.emit(source, None)
        else:
            if name in self.tile_color_palettes.keys():
                command = cmdRemColPal(
                    self.tile_color_palettes, name, "Add color palette"
                )
                self.undo_stack.push(command)
            else:
                self.col_pal_removed.emit(source, None)

    def setPixBatch(self, batch, source):
        """Sets pixels to new values based on the contents of a set of pixel deltas

        :param batch: Set of pixel deltas represented by pixel indexes and new values
        :type batch: defaultdict
        :param source: Subject source of pixels, either sprite or tile
        :type source: [type]
        """
        target = (
            self.sprite_pixel_palettes
            if source is Source.SPRITE
            else self.tile_pixel_palettes
        )
        command = cmdSetPixBatch(target, batch, "Draw pixels")
        self.undo_stack.push(command)

    def addPixRow(self, source):
        """Add a new row of sprites or tiles

        :param source: Subject source to add the row to, either sprite or tile
        :type source: Source
        """
        target = (
            self.sprite_pixel_palettes
            if source is Source.SPRITE
            else self.tile_pixel_palettes
        )
        target_name = "sprite" if source is Source.SPRITE else "tile"
        command = cmdAddPixRow(target, "Add {} row".format(target_name))
        self.undo_stack.push(command)

    def remPixRow(self, source):
        """Remove a row of sprites or tiles

        :param source: Subject source to remove the row from, either sprite or tile
        :type source: Source
        """
        target = (
            self.sprite_pixel_palettes
            if source is Source.SPRITE
            else self.tile_pixel_palettes
        )
        target_name = "sprite" if source is Source.SPRITE else "tile"
        command = cmdRemPixRow(target, "Add {} row".format(target_name))
        self.undo_stack.push(command)

    def setUndoStack(self, undo_stack):
        """Sets the undo stack for the GameData object

        :param undo_stack: The undo stack to set
        :type undo_stack: QUndoStack
        """
        self.undo_stack = undo_stack

    @classmethod
    def fromFilename(cls, file_name, parent=None):
        """Class method to instantiate the GameData object from a JSON file containing project data

        :param file_name: Path to project data JSON file
        :type file_name: str
        :param parent: Parent widget for GameData object, defaults to None
        :type parent: QWidget, optional
        :return: Instance of GameData instantiated with data from file
        :rtype: GameData
        """
        with open(file_name, "r") as data_file:
            return cls(json.load(data_file), parent)
