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
        zoomFactor = 2
        oldPos = event.scenePos()

        detail = QStyleOptionGraphicsItem.levelOfDetailFromTransform(self.transform())
        if detail < 100 and event.delta() > 0:
            self.scale(zoomFactor, zoomFactor)
        if detail > 10 and event.delta() < 0:
            self.scale((1 / zoomFactor), (1 / zoomFactor))

        newPos = event.scenePos()
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

class Overlay(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        self.start_pos = None
        self.last_pos = None
        self.tool = None
        self.width = 8
        self.height = 8
        self.color = 0
        self.filled = False
        self.setColor(self.color)
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap, parent)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)

    def setFill(self, filled):
        self.filled = filled

    def setTool(self, tool):
        self.tool = tool

    def setColor(self, color):
        self.color = color

    def setWidth(self, width):
        self.width = width
        self.setPixmap(self.pixmap().scaled(self.width, self.height))

    def setHeight(self, height):
        self.height = height
        self.setPixmap(self.pixmap().scaled(self.width, self.height))

    def clear(self):
        pixmap = self.pixmap()
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.start_pos is None:
                self.start_pos = QPointF(math.floor(event.pos().x()), math.floor(event.pos().y()))
                self.last_pos = self.start_pos
                if self.tool is Tools.PEN:
                    pixmap = self.pixmap()
                    painter = QPainter(pixmap)
                    pen = QPen(QColor.fromRgba(self.color))
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawPoint(self.start_pos)
                    self.setPixmap(pixmap)
                    painter.end()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.tool in [Tools.LINE, Tools.RECTANGLE, Tools.ELLIPSE]:
                self.clear()
            pixmap = self.pixmap()
            painter = QPainter(pixmap)
            cur_pos = QPointF(math.floor(event.pos().x()), math.floor(event.pos().y()))
            pen = QPen(QColor.fromRgba(self.color))
            pen.setWidth(1)
            painter.setPen(pen)
            if(self.filled):
                brush = QBrush(QColor.fromRgba(self.color))
                painter.setBrush(brush)
            if self.tool is Tools.LINE:
                painter.drawLine(self.start_pos, cur_pos)
            elif self.tool is Tools.ELLIPSE:
                painter.drawEllipse(QRectF(self.start_pos, cur_pos))
            elif self.tool is Tools.RECTANGLE:
                painter.drawRect(QRectF(self.start_pos, cur_pos))
            elif self.tool is Tools.PEN:
                painter.drawLine(self.last_pos, cur_pos)
            self.setPixmap(pixmap)
            self.last_pos = cur_pos
            painter.end()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        if event.button() == Qt.LeftButton:
            self.scene.bakeOverlay(self.pixmap().toImage())

class Subject(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        self.root = 0
        self.width = 8
        self.height = 8
        self.color_table = [0]*16
        self.subject = QImage(bytes([0]*self.width*self.height), self.width, self.height, QImage.Format_Indexed8)
        self.setColorTable(self.color_table)
        super().__init__(QPixmap.fromImage(self.subject), parent)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)

    def setPixel(self, x, y, value):
        self.subject.setPixel(x, y, value)

    def setColorTable(self, colors):
        self.color_table = colors
        self.subject.setColorCount(16)
        self.subject.setColorTable(self.color_table)

    def update(self):
        self.setPixmap(QPixmap.fromImage(self.subject))

    def setRoot(self, root):
        self.root = root

    def setWidth(self, width):
        self.width = width
        self.resizeSubject()

    def setHeight(self, height):
        self.height = height
        self.resizeSubject()

    def resizeSubject(self):
        self.subject = QImage(bytes([0]*self.width*self.height), self.width, self.height, QImage.Format_Indexed8)
        self.setColorTable(self.color_table)

class GraphicsScene(QGraphicsScene):
    def __init__(self, data, source, parent=None):
        super().__init__(parent)
        self.data = data
        self.source = source
        self.current_color_palette = None
        self.subject = Subject()
        self.overlay = Overlay()
        self.overlay.scene = self
        self.overlay.setTool(Tools.PEN)
        self.addItem(self.subject)
        self.addItem(self.overlay)
        self.primary_color = 0
        self.setTool(Tools.PEN)
        self.drawing = False

    @pyqtSlot(int, int, int)
    def setSubject(self, root, width, height):
        self.subject.setRoot(root)
        self.subject.setWidth(width * 8)
        self.subject.setHeight(height * 8)
        self.overlay.setWidth(width * 8)
        self.overlay.setHeight(height * 8)
        data = list(self.data.getSprites()) if self.source == Sources.SPRITE else list(self.data.getTiles())
        for row in range(height):
            for col in range(width):
                cur_subject = data[root + col + (row * 16)]
                for y in range(8):
                    for x in range(8):
                        self.subject.setPixel(8*col+x, 8*row+y, cur_subject[y][x])

        self.subject.update()
        self.overlay.update()
        self.setSceneRect(self.itemsBoundingRect())

    @pyqtSlot(str)
    def setPalette(self, source):
        self.current_color_palette = self.data.getSprColPal(source)
        self.subject.setColorTable([color.rgba() for color in self.current_color_palette])
        self.subject.update()

    @pyqtSlot(Tools)
    def setTool(self, tool):
        self.tool = tool

    @pyqtSlot(int)
    def setPrimaryColor(self, color):
        self.primary_color = color
        self.overlay.setColor(self.current_color_palette[self.primary_color].rgba())

    def bakeOverlay(self, overlay):
        for row in range(overlay.height()):
            for col in range(overlay.width()):
                if overlay.pixel(col, row) != 0:
                    pass

    def drawForeground(self, painter, rect):
        pen = QPen(Qt.darkCyan)
        pen.setWidth(0)
        painter.setPen(pen)
        lines = []
        for longitude in range(self.subject.width + 1):
            line = QLineF(longitude, 0, longitude, self.subject.height)
            lines.append(line)
        for latitude in range(self.subject.height + 1):
            line = QLineF(0, latitude, self.subject.width, latitude)
            lines.append(line)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        painter.setBrush(QBrush(Qt.magenta, Qt.SolidPattern))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.subject.width, self.subject.height)