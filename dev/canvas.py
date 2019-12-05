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
    def __init__(self, data, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.data = data
        self.pen_color = 0
        self.setTool(Tools.PEN)

    def setCanvas(self, source):
        sprite = self.data.getSprite(source)
        self.canvas = QImage(bytes([pix for sub in sprite for pix in sub]), 8, 8, QImage.Format_Indexed8)

    pyqtSlot(str)
    def setPalette(self, source):
        palette = self.data.getSprColPal(source)
        self.canvas.setColorTable([color.rgba() for color in palette])
        self.items()[0].setPixmap(QPixmap.fromImage(self.canvas))

    def showSprite(self):
        sprite = QGraphicsPixmapItem(QPixmap.fromImage(self.canvas))
        sprite.mousePressEvent = self.draw
        self.addItem(sprite)

    def setTool(self, tool):
        self.tool = tool

    def draw(self, event):
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        #self.draw_pixel.emit("sprite80", row, col, self.pen_color)

    def drawForeground(self, painter, rect):
        pen = QPen(Qt.darkCyan)
        pen.setWidth(0)
        painter.setPen(pen)
        lines = []
        for longitude in range(9):
            line = QLineF(0, longitude, 8, longitude)
            lines.append(line)
        for latitude in range(9):
            line = QLineF(latitude, 0, latitude, 8)
            lines.append(line)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        painter.setBrush(QBrush(Qt.magenta, Qt.SolidPattern))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, 8, 8)