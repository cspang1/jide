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

class GraphicsScene(QGraphicsScene):
    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.subject = QImage(bytes([0]*64), 8, 8, QImage.Format_Indexed8)
        self.subject.setColorCount(16)
        self.source = source
        subject_item = QGraphicsPixmapItem(QPixmap.fromImage(self.subject))
        subject_item.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        subject_item.mousePressEvent = self.draw
        subject_item.mouseReleaseEvent = self.release
        subject_item.mouseMoveEvent = self.drag
        self.addItem(subject_item)
        self.data = data
        self.data.spr_pix_updated.connect(self.updatePixel)
        self.pen_color = 0
        self.setTool(Tools.PEN)
        self.drawing = False

    @pyqtSlot(str)
    def setSubject(self, source):
        self.subject_name = source
        subject = self.data.getSprite(source) if self.source == Sources.SPRITE else self.data.getTile(source)
        for row in range(8):
            for col in range(8):
                self.subject.setPixel(col, row, subject[row][col])
        self.updateSubject()

    @pyqtSlot(str)
    def setPalette(self, source):
        palette = self.data.getSprColPal(source)
        self.subject.setColorTable([color.rgba() for color in palette])
        self.updateSubject()

    @pyqtSlot(int, int)
    def updatePixel(self, row, col):
        data = self.data.getSprite(self.subject_name) if self.source == Sources.SPRITE else self.data.getTile(self.subject_name)
        self.subject.setPixel(col, row, data[row][col])
        self.updateSubject()

    def updateSubject(self):
        self.items()[0].setPixmap(QPixmap.fromImage(self.subject))

    def setTool(self, tool):
        self.tool = tool

    @pyqtSlot(int)
    def setPenColor(self, color):
        self.pen_color = color

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