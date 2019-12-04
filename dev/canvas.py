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
        self.scale(50, 50)

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
        if detail < 100 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > 10 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class GraphicsScene(QGraphicsScene):
    draw_pixel = pyqtSignal(str, int, int, int)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.canvas = None
        self.pixels = [[0]*8]*8
        self.palette = [qRgb(0,0,0)]*16
        self.pen_color = Qt.black
        self.setTool(Tools.PEN)

    def setCanvas(self, source):
        self.pixels = source

    def setPalette(self, source):
        self.palette = source

    def showSprite(self):
        self.canvas = QImage(bytes([pix for sub in self.pixels for pix in sub]), 8, 8, QImage.Format_Indexed8)
        self.canvas.setColorTable(self.palette)
        sprite = QGraphicsPixmapItem(QPixmap.fromImage(self.canvas))
        sprite.mousePressEvent = self.draw
        self.addItem(sprite)

    def setTool(self, tool):
        self.tool = tool

    def draw(self, event):
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        value = 2
        self.draw_pixel.emit("sprite80", row, col, value)

    @pyqtSlot(QColor)
    def changeColor(self, color):
        self.pen_color = color

    @pyqtSlot(int, int)
    def update(self, row, col):
        pass