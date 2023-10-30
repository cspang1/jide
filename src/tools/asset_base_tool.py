from enum import Enum
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QObject

class AssetToolType(Enum):
    ARROW = 0 #TODO?
    SELECT = 1
    MOVE = 2 #TODO
    PEN = 3
    FILL = 4
    LINE = 5
    RECTANGLE = 6
    ELLIPSE = 7
    PASTE = 8 #TODO

class AssetBaseTool(QObject):
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def mousePressEvent(self, event: QMouseEvent) -> None: ...

    def mouseMoveEvent(self, event: QMouseEvent) -> None: ...

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...
