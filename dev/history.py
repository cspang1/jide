from collections import defaultdict
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QUndoCommand, QUndoStack

class cmdSetCol(QUndoCommand):
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

class cmdSetColPalName(QUndoCommand):
    def __init__(self, palette, cur_name, new_name, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.cur_name = cur_name
        self.new_name = new_name

    def redo(self):
        self.palette.setName(self.cur_name, self.new_name)

    def undo(self):
        self.palette.setName(self.new_name, self.cur_name)

class cmdAddColPal(QUndoCommand):
    def __init__(self, palette, name, contents, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.name = name
        self.contents = contents

    def redo(self):
        self.palette.addPalette(self.name, self.contents)

    def undo(self):
        self.palette.remPalette(self.name)

class cmdRemColPal(QUndoCommand):
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

class cmdSetPixBatch(QUndoCommand):
    def __init__(self, palette, batch, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.batch = batch
        self.original_batch = defaultdict(list)

    def redo(self):
        for index, updates in self.batch.items():
            for row, col, val in updates:
                self.original_batch[index].append((row, col, self.palette[index][row][col]))
                self.palette[index, row, col] = val
        self.palette.batchUpdate()

    def undo(self):
        for index, updates in self.original_batch.items():
            for row, col, val in updates:
                self.palette[index, row, col] = val
        self.palette.batchUpdate()

class cmdAddPixRow(QUndoCommand):
    def __init__(self, palette, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette

    def redo(self):
        self.palette.addRow()

    def undo(self):
        self.palette.remRow()

class cmdRemPixRow(QUndoCommand):
    def __init__(self, palette, description, parent=None):
        super().__init__(description, parent)
        self.palette = palette
        self.row = []

    def redo(self):
        self.row = self.palette.remRow()

    def undo(self):
        self.palette.addRow(self.row)