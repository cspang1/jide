import sys
from PyQt5.QtCore import Qt, QRectF, QEvent
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QStyleOptionGraphicsItem

class EditorView(QGraphicsView):
    """QGraphicsView into sprite/tile canvas

    :param scene:   QGraphicsScene representing sprite/tile canvas
    :type scene:    QGraphicsScene, defaults to None
    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(50, 50)
        self.setEnabled(True)

    def eventFilter(self, source, event):
        """Event filter for handling zoom/pan events

        :param source:  Source of event
        :type source:   QObject
        :param event:   Triggered event
        :type event:    QEvent
        :return:        Whether to continue processing event downstream
        :rtype:         bool
        """
        if event.type() == QEvent.GraphicsSceneWheel:
            self.zoomCanvas(event)
            event.accept()
            return True
        return False

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
        if detail > 10 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
    
    def setScene(self, scene: QGraphicsScene) -> None:
        super().setScene(scene)
        self.scene().installEventFilter(self)
