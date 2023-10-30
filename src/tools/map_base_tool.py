from enum import Enum
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QObject

class MapToolType(Enum):
    ARROW = 0
    SELECT = 1
    MOVE = 2
    TILE = 3
    FILL = 4
    PASTE = 5

class MapBaseTool(QObject):
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def mousePressEvent(self, event: QMouseEvent) -> None: ...

    def mouseMoveEvent(self, event: QMouseEvent) -> None: ...

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...
