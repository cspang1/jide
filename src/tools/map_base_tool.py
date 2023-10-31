from enum import Enum
from PyQt5.QtGui import (
    QMouseEvent,
    QImage
)
from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)

class MapToolType(Enum):
    SELECT = 0
    TILE = 1
    PASTE = 2

class MapBaseTool(QObject):

    scene_edited = pyqtSignal(QImage)
    
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def mousePressEvent(self, event: QMouseEvent) -> None: ...

    def mouseMoveEvent(self, event: QMouseEvent) -> None: ...

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...
