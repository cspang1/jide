from collections import defaultdict
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QUndoCommand, QUndoStack


class cmdSetCol(QUndoCommand):
    """Sets a color in a color palette

    :param palette: Target set of color palettes
    :type palette: gamedata.ColorPalettes
    :param name: Name of target color palette
    :type name: str
    :param index: Index of target color
    :type index: int
    :param color: New color to set to
    :type color: QColor
    :param orig: Original color
    :type orig: QColor
    :param description: Text description of action
    :type description: Str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, name, index, color, orig, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.index = index
        self.color = color
        self.original_color = orig if orig is not None else self.palette[name][index]

    def redo(self):
        """Redo setting a color
        """
        self.palette[self.name, self.index] = self.color

    def undo(self):
        """Undo setting a color
        """
        self.palette[self.name, self.index] = self.original_color


class cmdSetColPalName(QUndoCommand):
    """Set the name of a color palette

    :param palette: Target set of color palettes
    :type palette: gamedata.ColorPalettes
    :param cur_name: Target name of color palette
    :type cur_name: str
    :param new_name: New name for color palette
    :type new_name: str
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, cur_name, new_name, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.cur_name = cur_name
        self.new_name = new_name

    def redo(self):
        """Redo setting a color palette name
        """
        self.palette.setName(self.cur_name, self.new_name)

    def undo(self):
        """Undo setting a color palette name
        """
        self.palette.setName(self.new_name, self.cur_name)


class cmdAddColPal(QUndoCommand):
    """Add a new sprite/tile color palette

    :param palette: Target set of color palettes
    :type palette: gamedata.ColorPalettes
    :param name: Name of target color palette
    :type name: str
    :param contents: Contents of new color palette
    :type contents: list
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, name, contents, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.contents = contents

    def redo(self):
        """Redo adding a color palette
        """
        self.palette.addPalette(self.name, self.contents)

    def undo(self):
        """Undo adding a color palette
        """
        self.palette.remPalette(self.name)


class cmdRemColPal(QUndoCommand):
    """Remove a sprite/tile color palette

    :param palette: Target set of color palettes
    :type palette: gamedata.ColorPalettes
    :param name: Name of target color palette
    :type name: str
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, name, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.contents = self.palette[self.name]
        self.index = list(self.palette.keys()).index(self.name)

    def redo(self):
        """Redo removing a color palette
        """
        self.palette.remPalette(self.name)

    def undo(self):
        """Undo removing a color palette
        """
        self.palette.addPalette(self.name, self.contents, self.index)


class cmdSetPixBatch(QUndoCommand):
    """Apply a pixel batch update

    :param palette: Target set of pixel palettes
    :type palette: gamedata.PixelPalettes
    :param batch: Set of pixel deltas represented by pixel indexes and new values
    :type batch: defaultdict
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, batch, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.batch = batch
        self.original_batch = defaultdict(list)

    def redo(self):
        """Redo updating with a pixel batch
        """
        for index, updates in self.batch.items():
            for row, col, val in updates:
                self.original_batch[index].append(
                    (row, col, self.palette[index][row][col])
                )
                self.palette[index, row, col] = val
        self.palette.batchUpdate()

    def undo(self):
        """Undo updating with a pixel batch
        """
        for index, updates in self.original_batch.items():
            for row, col, val in updates:
                self.palette[index, row, col] = val
        self.palette.batchUpdate()


class cmdAddPixRow(QUndoCommand):
    """Add a row of sprite/tiles to a pixel palette

    :param palette: Target set of pixel palettes
    :type palette: gamedata.PixelPalettes
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette

    def redo(self):
        """Redo adding a row of sprites/tiles
        """
        self.palette.addRow()

    def undo(self):
        """Undo addign a row of sprites/tiles
        """
        self.palette.remRow()


class cmdRemPixRow(QUndoCommand):
    """Remove a row of sprite/tiles from a pixel palette

    :param palette: Target set of pixel palettes
    :type palette: gamedata.PixelPalettes
    :param description: Text description of action
    :type description: str
    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional
    """

    def __init__(self, palette, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.row = []

    def redo(self):
        """Redo removing a row of sprites/tiles
        """
        self.row = self.palette.remRow()

    def undo(self):
        """Undo removing a row of sprites/tiles
        """
        self.palette.addRow(self.row)
