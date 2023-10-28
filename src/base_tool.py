from enum import Enum

class ToolType(Enum):
    NONE = 0
    SELECT = 1
    PEN = 2
    FILL = 3
    LINE = 4
    RECTANGLE = 5
    ELLIPSE = 6

class BaseTool:
    def __init__(self, view):
        self.set_view(view)
        self.color = None

    def set_view(self, view):
        self.view = view

    def set_color(self, color):
        self.color = color

    def mousePressEvent(self, event): ...

    def mouseMoveEvent(self, event): ...

    def mouseReleaseEvent(self, event): ...