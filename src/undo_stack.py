from PyQt5.QtWidgets import QUndoStack
from PyQt5.QtCore import pyqtSignal
from collections import namedtuple

Validator = namedtuple('Validator', ['is_valid', 'validation_error'])

class UndoStack(QUndoStack):

    error_thrown = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def push(self, command):
        is_valid, validation_error = command.validate()
        if is_valid:
            super().push(command)
        else:
            if validation_error:
                self.error_thrown.emit(validation_error)
