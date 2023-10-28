from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSlot,
    pyqtSignal,
    QRect
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QStyleOptionGraphicsItem
)
from PyQt5.QtGui import (
    QColor,
    QImage
)
from base_tool import ToolType
from pen_tool import PenTool
from select_tool import SelectTool
from arrow_tool import ArrowTool

class EditorView(QGraphicsView):

    scene_edited = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(50, 50)
        self.setEnabled(True)
        self.panning = False
        self.selection = None
        self.last_pos = None
        self.active_tool = None
        self.tools = {
            ToolType.ARROW: ArrowTool(self),
            ToolType.SELECT: SelectTool(self),
            ToolType.PEN: PenTool(self),
            # ToolType.FILL: PenTool(self, None),
            # ToolType.LINE: PenTool(self, None),
            # ToolType.RECTANGLE: RectangleTool(self.scene),
            # ToolType.ELLIPSE: EllipseTool(self.scene)
        }

        self.tools[ToolType.PEN].scene_edited.connect(self.scene_edited)
        # self.tools[ToolType.FILL].scene_edited.connect(self.scene_edited)
        # self.tools[ToolType.LINE].scene_edited.connect(self.scene_edited)
        # self.tools[ToolType.RECTANGLE].scene_edited.connect(self.scene_edited)
        # self.tools[ToolType.ELLIPSE].scene_edited.connect(self.scene_edited)

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

        if event.buttons() == Qt.LeftButton:
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

    @pyqtSlot(QColor, int)
    def set_tool_color(self, color, color_index):
        self.tools[ToolType.PEN].set_color(color, color_index)
        # self.tools[ToolType.FILL].set_color(color)
        # self.tools[ToolType.LINE].set_color(color)
        # self.tools[ToolType.RECTANGLE].set_color(color)
        # self.tools[ToolType.ELLIPSE].set_color(color)

    def setScene(self, scene: QGraphicsScene) -> None:
        super().setScene(scene)
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

    def get_selection(self):
        return self.selection
    
    def set_selection(self, selection):
        self.selection = selection

    def clear_selection(self):
        self.set_selection(None)
        self.tools[ToolType.SELECT].remove_selection_box()
