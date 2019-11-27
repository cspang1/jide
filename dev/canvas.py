from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPalette, QColor, QIcon, QPen, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QEvent
from canvastools import Tools
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
        return False

    def zoomCanvas(self, event):
        zoomFactor = 1.25
        oldPos = event.scenePos()

        detail = QStyleOptionGraphicsItem.levelOfDetailFromTransform(self.transform())
        if detail < 10 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > .1 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 800, 800)
        self.addRect(0,0,800,800,Qt.magenta,Qt.magenta)
        self.tool = Tools.PEN

    def setTool(self, tool):
        self.tool = tool

    def mousePressEvent(self, event):
        if self.tool is Tools.PEN:
            self.drawPixel(event)

    def drawPixel(self, event):
        pen = QPen(Qt.black, Qt.MiterJoin)
        brush = QBrush(Qt.black)
        x = math.floor(event.scenePos().x()/100)*100
        y = math.floor(event.scenePos().y()/100)*100
        if 0 <= x < 800 and 0 <= y < 800:
            self.addRect(x, y, 100, 100, pen, brush)