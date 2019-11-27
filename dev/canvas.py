from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from canvastools import Tools
from itertools import product
from typing import List
from dataclasses import dataclass, field
import sys
import os
import math

@dataclass
class pixels(QObject):
    data: List[Qt.GlobalColor]
    data_changed = pyqtSignal(int, int)

    def __init__(self, data=[[]]):
        QObject.__init__(self)
        self.data = data

    def __getitem__(self, index):
        row, col = index
        return self.data[row][col]

    def __setitem__(self, index, value):
        row, col = index
        self.data[row][col] = value
        self.data_changed.emit(row, col)

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.scene = GraphicsScene(self)
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
    pix = pixels([[Qt.magenta]*8]*8)
    pen_color = Qt.black

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 700, 700)
        for row in range(8):
            for column in range(8):
                self.addRect(row*100, column*100, 100, 100, self.pix[row,column], self.pix[row,column])
        self.tool = Tools.PEN
        self.pix.data_changed.connect(self.update)

    @pyqtSlot(QColor)
    def changeColor(self, color):
        self.pen_color = color

    @pyqtSlot(int, int)
    def update(self, row, col):
        pen = QPen(self.pix[row, col], Qt.MiterJoin)
        brush = QBrush(self.pix[row, col])
        pixel = self.itemAt(row*100, col*100, QtGui.QTransform())
        pixel.setPen(pen)
        pixel.setBrush(brush)

    def setTool(self, tool):
        self.tool = tool

    def mousePressEvent(self, event):
        if self.tool is Tools.PEN and 0 < event.scenePos().x() < 800 and 0 < event.scenePos().y() < 800:
            x = math.floor(event.scenePos().x()/100)
            y = math.floor(event.scenePos().y()/100)
            self.pix[x,y] = self.pen_color
