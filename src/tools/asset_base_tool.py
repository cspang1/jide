from enum import Enum
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QObject

class AssetToolType(Enum):
    ARROW = 0
    SELECT = 1
    PEN = 2
    FILL = 3
    LINE = 4
    RECTANGLE = 5
    ELLIPSE = 6

class AssetBaseTool(QObject):
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def mousePressEvent(self, event: QMouseEvent) -> None: ...

    def mouseMoveEvent(self, event: QMouseEvent) -> None: ...

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...
