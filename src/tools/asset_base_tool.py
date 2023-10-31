from enum import Enum
from PyQt5.QtGui import (
    QMouseEvent,
    QImage
)
from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)

class AssetToolType(Enum):
    SELECT = 0
    PEN = 1
    FILL = 2
    LINE = 3
    RECTANGLE = 4
    ELLIPSE = 5
    PASTE = 6

class AssetBaseTool(QObject):

    scene_edited = pyqtSignal(QImage)
    
    def __init__(self, view):
        super().__init__(view)
        self.view = view

    def mousePressEvent(self, event: QMouseEvent) -> None: ...

    def mouseMoveEvent(self, event: QMouseEvent) -> None: ...

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...

    def set_color(self, color, color_index):
        self.color = color
        self.color_index = color_index
