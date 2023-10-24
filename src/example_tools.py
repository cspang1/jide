import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QAction
from PyQt5.QtCore import Qt
from enum import Enum

class ToolType(Enum):
    SELECT = 1
    PEN = 2
    ELLIPSE = 3
    RECTANGLE = 4

class BaseTool:
    def __init__(self, scene):
        self.scene = scene

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class SelectTool(BaseTool):
    def mousePressEvent(self, event):
        # Select logic
        pass

class PenTool(BaseTool):
    def mousePressEvent(self, event):
        # Pen drawing logic
        pass

class EllipseTool(BaseTool):
    def mousePressEvent(self, event):
        # Ellipse drawing logic
        pass

class RectangleTool(BaseTool):
    def mousePressEvent(self, event):
        # Rectangle drawing logic
        pass

class GraphicsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create QGraphicsScene, QGraphicsView, and set up UI
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Create tool instances
        self.active_tool = None
        self.tools = {
            ToolType.SELECT: SelectTool(self.scene),
            ToolType.PEN: PenTool(self.scene),
            ToolType.ELLIPSE: EllipseTool(self.scene),
            ToolType.RECTANGLE: RectangleTool(self.scene),
        }

        # Set up actions for selecting tools
        self.tool_actions = {}
        for tool_type, tool_class in self.tools.items():
            action = QAction(tool_type.name, self)
            action.setCheckable(True)
            action.triggered.connect(self.activate_tool)
            self.tool_actions[tool_type] = action
            self.addAction(action)

    def activate_tool(self):
        sender = self.sender()
        for tool_type, action in self.tool_actions.items():
            if action == sender:
                self.active_tool = self.tools[tool_type]

    # Implement event handling methods, e.g., mousePressEvent, mouseMoveEvent, mouseReleaseEvent

def main():
    app = QApplication(sys.argv)
    editor = GraphicsEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
