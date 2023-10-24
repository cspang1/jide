from PyQt5.QtCore import Qt, QEvent, QPointF
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QStyleOptionGraphicsItem
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

    def setScene(self, scene: QGraphicsScene) -> None:
        super().setScene(scene)
        self.scene().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel:
            self.zoomCanvas(event)
            event.accept()
            return True

        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.last_pos = event.pos()
            self.panning = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def zoomCanvas(self, event):
        """Zoom view into sprite/tile canvas

        :param event:   Source event
        :type event:    QEvent
        """
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
