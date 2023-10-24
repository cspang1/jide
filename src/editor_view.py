from PyQt5.QtCore import (
    Qt,
    QEvent
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QStyleOptionGraphicsItem
)
from pixel_tools import (
    ToolType,
    PenTool
)

class EditorView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(50, 50)
        self.setEnabled(True)
        self.panning = False
        self.last_pos = None
        self.pen_tool = PenTool(self,self.scene(), Qt.red)

    def setScene(self, scene: QGraphicsScene) -> None:
        super().setScene(scene)
        self.pen_tool.set_scene(self.scene())
        self.scene().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel:
            self.zoomCanvas(event)
            event.accept()
            return True

        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MiddleButton:
            self.last_pos = event.pos()
            self.panning = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.ClosedHandCursor)
        self.pen_tool.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.panning:
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        self.pen_tool.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
        self.pen_tool.mouseReleaseEvent(event)

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
