from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSlot,
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QStyleOptionGraphicsItem,
    QApplication
)
from PyQt5.QtGui import (
    QColor,
    QImage,
    QMouseEvent
)
from tools.asset_base_tool import AssetToolType
from tools.asset_pen_tool import AssetPenTool
from tools.asset_select_tool import AssetSelectTool
from tools.asset_arrow_tool import AssetArrowTool
from tools.asset_line_tool import AssetLineTool
from tools.asset_rectangle_tool import AssetRectangleTool
from tools.asset_ellipse_tool import AssetEllipseTool
from tools.asset_fill_tool import AssetFillTool
from tools.asset_paste_tool import AssetPasteTool

class EditorView(QGraphicsView):

    scene_edited = pyqtSignal(QImage)
    selection_made = pyqtSignal(bool)
    selection_copied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(50, 50)
        self.setEnabled(True)
        self.selection = None
        self.last_pos = None
        self.current_pos = None
        self.active_tool = None
        self.temp_tool = None
        self.tools = {
            AssetToolType.ARROW: AssetArrowTool(self),
            AssetToolType.SELECT: AssetSelectTool(self),
            AssetToolType.PEN: AssetPenTool(self),
            AssetToolType.LINE: AssetLineTool(self),
            AssetToolType.RECTANGLE: AssetRectangleTool(self),
            AssetToolType.ELLIPSE: AssetEllipseTool(self),
            AssetToolType.FILL: AssetFillTool(self),
            AssetToolType.PASTE: AssetPasteTool(self)
        }

        self.tools[AssetToolType.PEN].scene_edited.connect(self.scene_edited)
        self.tools[AssetToolType.LINE].scene_edited.connect(self.scene_edited)
        self.tools[AssetToolType.RECTANGLE].scene_edited.connect(self.scene_edited)
        self.tools[AssetToolType.ELLIPSE].scene_edited.connect(self.scene_edited)
        self.tools[AssetToolType.FILL].scene_edited.connect(self.scene_edited)
        self.tools[AssetToolType.PASTE].scene_edited.connect(self.scene_edited)

        #TODO: Implement an overlay where each pixel's index is displayed

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MiddleButton:
            self.last_pos = event.pos()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.ClosedHandCursor)

        if event.button() == Qt.LeftButton:
            self.tools[self.active_tool].mousePressEvent(event)

        if self.active_tool == AssetToolType.PASTE:
            self.active_tool = self.temp_tool

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.MiddleButton:
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

        self.current_pos = event.pos()
        if event.buttons() == Qt.LeftButton or self.active_tool == AssetToolType.PASTE:
            self.tools[self.active_tool].mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().setCursor(Qt.ArrowCursor)

        if event.button() == Qt.LeftButton:
            self.tools[self.active_tool].mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.active_tool == AssetToolType.PASTE:
            self.tools[self.active_tool].abort_paste()
            self.active_tool = self.temp_tool
            self.update()
            return

        super().keyPressEvent(event)

    def enterEvent(self, event):
        self.setCursor(Qt.CrossCursor)

    def leaveEvent(self, event):
        self.unsetCursor()

    def setScene(self, scene):
        super().setScene(scene)
        self.scene().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel:
            self.zoom_canvas(event)
            event.accept()
            return True

        return super().eventFilter(source, event)

    @pyqtSlot(AssetToolType)
    def set_tool(self, tool):
        self.active_tool = tool

    @pyqtSlot(QColor, int)
    def set_tool_color(self, color, color_index):
        self.tools[AssetToolType.PEN].set_color(color, color_index)
        self.tools[AssetToolType.LINE].set_color(color, color_index)
        self.tools[AssetToolType.RECTANGLE].set_color(color, color_index)
        self.tools[AssetToolType.ELLIPSE].set_color(color, color_index)
        self.tools[AssetToolType.FILL].set_color(color, color_index)

    def zoom_canvas(self, event):
        zoomFactor = 2
        last_pos = event.scenePos()

        detail = QStyleOptionGraphicsItem.levelOfDetailFromTransform(
            self.transform()
        )
        if detail < 100 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > 5 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        current_pos = event.scenePos()
        delta = current_pos - last_pos
        self.translate(delta.x(), delta.y())

    def get_selection(self):
        return self.selection
    
    def set_selection(self, selection):
        self.selection = selection
        self.selection_made.emit(self.selection is not None)

    def clear_selection(self):
        self.set_selection(None)
        self.tools[AssetToolType.SELECT].remove_selection_box()

    def copy(self):
        QApplication.clipboard().setImage(
            self.scene().get_image(True).copy(self.get_selection())
        )
        self.selection_copied.emit()

    def paste(self):
        if self.active_tool == AssetToolType.PASTE:
            return

        self.clear_selection()
        self.temp_tool = self.active_tool
        self.active_tool = AssetToolType.PASTE

        self.tools[self.active_tool].mouseMoveEvent(
            QMouseEvent(QMouseEvent.MouseMove, self.current_pos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        )
