from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QStyleOptionGraphicsItem
)
from PyQt5.QtGui import QColor
from base_tool import (
    BaseTool,
    ToolType
)
from pen_tool import PenTool
from select_tool import SelectTool

class EditorView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(50, 50)
        self.setEnabled(True)
        self.panning = False
        self.last_pos = None
        self.active_tool = None
        self.tools = {
            ToolType.NONE: BaseTool(self),
            ToolType.SELECT: SelectTool(self),
            ToolType.PEN: PenTool(self),
            # ToolType.FILL: PenTool(self, None),
            # ToolType.LINE: PenTool(self, None),
            # ToolType.RECTANGLE: RectangleTool(self.scene),
            # ToolType.ELLIPSE: EllipseTool(self.scene)
        }

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MiddleButton:
            self.last_pos = event.pos()
            self.panning = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.ClosedHandCursor)

        if event.button() == Qt.LeftButton:
            self.tools[self.active_tool].mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.panning:
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

        self.tools[self.active_tool].mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            self.tools[self.active_tool].mouseReleaseEvent(event)

    @pyqtSlot(ToolType)
    def set_tool(self, tool):
        self.active_tool = tool

    @pyqtSlot(QColor)
    def set_tool_color(self, color):
        for tool in self.tools.values():
            tool.set_color(color)

    def setScene(self, scene: QGraphicsScene) -> None:
        super().setScene(scene)
        for tool in self.tools.values():
            tool.set_scene(self.scene())
        self.scene().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel:
            self.zoomCanvas(event)
            event.accept()
            return True

        return super().eventFilter(source, event)

    def zoomCanvas(self, event):
        zoomFactor = 2
        oldPos = event.scenePos()

        detail = QStyleOptionGraphicsItem.levelOfDetailFromTransform(
            self.transform()
        )
        if detail < 100 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > 5 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
