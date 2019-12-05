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
    update_pixel = pyqtSignal(str, int, int, int)

    def __init__(self, data, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.sprite = QImage(bytes([0]*64), 8, 8, QImage.Format_Indexed8)
        self.sprite.setColorCount(16)
        spriteItem = QGraphicsPixmapItem(QPixmap.fromImage(self.sprite))
        spriteItem.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        spriteItem.mousePressEvent = self.draw
        spriteItem.mouseReleaseEvent = self.release
        spriteItem.mouseMoveEvent = self.drag
        self.addItem(spriteItem)
        self.data = data
        self.data.spr_pix_updated.connect(self.updatePixel)
        self.update_pixel.connect(self.data.setSprPix)
        self.pen_color = 0
        self.setTool(Tools.PEN)

    def setSprite(self, source):
        self.sprite_name = source
        sprite = self.data.getSprite(source)
        for row in range(8):
            for col in range(8):
                self.sprite.setPixel(col, row, sprite[row][col])
        self.updateSprite()

    pyqtSlot(str)
    def setPalette(self, source):
        palette = self.data.getSprColPal(source)
        self.sprite.setColorTable([color.rgba() for color in palette])
        self.updateSprite()

    pyqtSlot(int, int)
    def updatePixel(self, row, col):
        self.sprite.setPixel(col, row, self.data.getSprite(self.sprite_name)[row][col])
        self.updateSprite()

    def updateSprite(self):
        self.items()[0].setPixmap(QPixmap.fromImage(self.sprite))

    def setTool(self, tool):
        self.tool = tool

    pyqtSlot(int)
    def setPenColor(self, color):
        self.pen_color = color

    def drag(self, event):
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        if self.drawing and (row, col) != self.last_pos and 0 <= col < 8 and 0 <= row < 8:
            self.draw(event)

    def draw(self, event):
        self.drawing = True
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        self.last_pos = (row, col)
        self.update_pixel.emit(self.sprite_name, row, col, self.pen_color)

    def release(self, event):
        self.drawing = False

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