from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class cmdSetSprCol(QUndoCommand):
    def __init__(self, palette, name, index, color, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.index = index
        self.color = color
        self.original_color = self.palette[name][index]

    def redo(self):
        self.palette[self.name, self.index] = self.color

    def undo(self):
        self.palette[self.name, self.index] = self.original_color

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