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

class GraphicsView(QGraphicsView):
    def __init__(self, scene=None, parent=None):
        QGraphicsView.__init__(self, parent)
        self.scene = scene
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
        self.canvas = None
        self.pixels = [[0]*8]*8
        self.palette = [qRgb(0,0,0)]*16
        self.pen_color = Qt.black
        self.setTool(Tools.PEN)

    def setCanvas(self, source):
        name = source.name
        self.pixels = source.pixels

    def setPalette(self, source):
        self.palette = source.colors

    def showSprite(self):
        self.canvas = QImage(bytes([pix for sub in self.pixels for pix in sub]), 8, 8, QImage.Format_Indexed8)
        self.canvas.setColorTable(self.palette)
        sprite = QGraphicsPixmapItem(QPixmap.fromImage(self.canvas))
        self.addItem(sprite)

    def setTool(self, tool):
        self.tool = tool

    def mousePressEvent(self, event):
        if self.tool is Tools.PEN and 0 < event.scenePos().x() < 800 and 0 < event.scenePos().y() < 800:
            x = math.floor(event.scenePos().x()/100)
            y = math.floor(event.scenePos().y()/100)
            self.pix[x,y] = self.pen_color

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