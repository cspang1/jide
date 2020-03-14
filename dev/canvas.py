from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from canvastools import Tools
from sources import Sources
from itertools import product
from typing import List
from dataclasses import dataclass, field
import sys
import os
import math

class GraphicsView(QGraphicsView):
    def __init__(self, scene=None, parent=None):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene().installEventFilter(self)
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

class Subject(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        self.root = 0
        self.width = 8
        self.height = 8
        self.subject = QImage(bytes([0]*64), self.width, self.height, QImage.Format_Indexed8)
        self.subject.setColorCount(16)
        super().__init__(QPixmap.fromImage(self.subject), parent)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)

    def setPixel(self, x, y, value):
        self.subject.setPixel(x, y, value)

    def setColorTable(self, colors):
        self.subject.setColorTable(colors)

    def update(self):
        self.setPixmap(QPixmap.fromImage(self.subject))

    def setRoot(self, root):
        self.root = root

    def setWidth(self, width):
        self.width = width
        self.subject = self.subject.scaledToWidth(self.width)

    def setHeight(self, height):
        self.height = height
        self.subject = self.subject.scaledToHeight(self.height)

    def mouseMoveEvent(self, event):
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        if (row, col) != self.last_pos and 0 <= col < self.width and 0 <= row < self.height:
            self.mousePressEvent(event)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            col = math.floor(event.pos().x())
            row = math.floor(event.pos().y())
            self.last_pos = (row, col)
            self.scene.pixelClicked(self.root, row, col)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene.pixelReleased()

class GraphicsScene(QGraphicsScene):
    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.data = data
        self.source = source
        self.subject = Subject()
        self.subject.scene = self
        self.subject.data = self.data
        self.addItem(self.subject)
        self.data.spr_pix_updated.connect(self.updatePixel)
        self.pen_color = 0
        self.setTool(Tools.PEN)
        self.drawing = False

    @pyqtSlot(int, int, int)
    def setSubject(self, root, width, height):
        self.subject.setRoot(root)
        self.subject.setWidth(width * 8)
        self.subject.setHeight(height * 8)
        data = list(self.data.getSprites()) if self.source == Sources.SPRITE else list(self.data.getTiles())
        for row in range(height):
            for col in range(width):
                cur_subject = data[root + col + (row * 16)] # STORE INSTEAD IN 2D ARRAY AS A BASIC CACHE FOR PIXEL EDITING
                for y in range(8):
                    for x in range(8):
                        self.subject.setPixel(8*col+x, 8*row+y, cur_subject[y][x])

        self.subject.update()

    @pyqtSlot(str)
    def setPalette(self, source):
        palette = self.data.getSprColPal(source)
        self.subject.setColorTable([color.rgba() for color in palette])
        self.subject.update()

    @pyqtSlot(str, int, int)
    def updatePixel(self, name, row, col):
        data = self.data.getSprite(name) if self.source == Sources.SPRITE else self.data.getTile(name)
        self.subject.setPixel(col, row, data[row][col])
        self.subject.update()

    def setTool(self, tool):
        self.tool = tool

    @pyqtSlot(int)
    def setPenColor(self, color):
        self.pen_color = color

    def pixelClicked(self, root, row, col):
        pass

    def pixelReleased(self):
        pass

    def drag(self, event):
        col = math.floor(event.pos().x())
        row = math.floor(event.pos().y())
        if self.drawing and (row, col) != self.last_pos and 0 <= col < 8 and 0 <= row < 8:
            self.draw(event)

    def draw(self, event):
        if event.buttons() == Qt.LeftButton:
            if not self.drawing:
                self.data.undo_stack.beginMacro("Draw pixels")
                self.drawing = True
            col = math.floor(event.pos().x())
            row = math.floor(event.pos().y())
            self.last_pos = (row, col)
            self.data.setSprPix(self.subject_name, row, col, self.pen_color)

    def release(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.data.undo_stack.endMacro()

    def drawForeground(self, painter, rect):
        pen = QPen(Qt.darkCyan)
        pen.setWidth(0)
        painter.setPen(pen)
        lines = []
        for longitude in range(self.subject.height + 1):
            line = QLineF(0, longitude, self.subject.height, longitude)
            lines.append(line)
        for latitude in range(self.subject.width + 1):
            line = QLineF(latitude, 0, latitude, self.subject.width)
            lines.append(line)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        painter.setBrush(QBrush(Qt.magenta, Qt.SolidPattern))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.subject.height, self.subject.width)