from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPalette, QColor, QIcon, QPen, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QEvent
import sys
import os
import math

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.scene = GraphicsScene()
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel and QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.zoomCanvas(event)
            event.accept()
            return True
        if event.type() == QEvent.GraphicsSceneMousePress:
            self.scene.drawPixel(event)
            event.accept()
            return True
        return False

    def zoomCanvas(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        oldPos = event.scenePos()
        if event.delta() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)
        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 800, 800)
        self.opt = ""

    def setOption(self, opt):
        self.opt = opt

    def drawPixel(self, event):
        pen = QPen(Qt.black)
        brush = QBrush(Qt.black)
        x = math.floor(event.scenePos().x()/100)*100
        y = math.floor(event.scenePos().y()/100)*100
        if 0 <= x < 800 and 0 <= y < 800:
            self.addRect(x, y, 100, 100, pen, brush)