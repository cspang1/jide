from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class cmdSetSprCol(QUndoCommand):
    def __init__(self, palette, name, index, color, orig, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.index = index
        self.color = color
        self.original_color = orig if orig is not None else self.palette[name][index]

    def redo(self):
        self.palette[self.name, self.index] = self.color

    def undo(self):
        self.palette[self.name, self.index] = self.original_color

class cmdSetSprColPalName(QUndoCommand):
    def __init__(self, palette, cur_name, new_name, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.cur_name = cur_name
        self.new_name = new_name

    def redo(self):
        self.palette.setName(self.cur_name, self.new_name)

    def undo(self):
        self.palette.setName(self.new_name, self.cur_name)

class cmdAddSprColPal(QUndoCommand):
    def __init__(self, palette, name, contents, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.contents = contents

    def redo(self):
        self.palette.addPalette(self.name, self.contents)

    def undo(self):
        self.palette.remPalette(self.name)

class cmdRemSprColPal(QUndoCommand):
    def __init__(self, palette, name, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.contents = self.palette[self.name]
        self.index = list(self.palette.keys()).index(self.name)

    def redo(self):
        self.palette.remPalette(self.name)

    def undo(self):
        self.palette.addPalette(self.name, self.contents, self.index)

class cmdSetSprPix(QUndoCommand):
    def __init__(self, palette, name, row, col, value, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.row = row
        self.col = col
        self.value = value
        self.original_value = self.palette[name, row, col]

    def redo(self):
        self.palette[self.name, self.row, self.col] = self.value

    def undo(self):
        self.palette[self.name, self.row, self.col] = self.original_value