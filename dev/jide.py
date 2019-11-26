from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPalette, QColor, QIcon, QPen, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QEvent
import sys
import os
import math

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 800, 800)
        self.opt = ""

    def setOption(self, opt):
        self.opt = opt

    def mousePressEvent(self, event):
        pen = QPen(Qt.black)
        brush = QBrush(Qt.black)
        x = math.floor(event.scenePos().x()/100)*100
        y = math.floor(event.scenePos().y()/100)*100
        if self.opt == "Generate" and x < 800 and y < 800:
            self.addRect(x, y, 100, 100, pen, brush)
        elif self.opt == "Select":
            print(x, y)

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(ui_path, "mainwindow.ui"), self)
        self.setWindowTitle("JIDE")

        self.scene = GraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene.installEventFilter(self)
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        group = QButtonGroup(self)
        group.addButton(self.radioButton)
        group.addButton(self.radioButton_2)

        group.buttonClicked.connect(lambda btn: self.scene.setOption(btn.text()))
        self.radioButton.setChecked(True)
        self.scene.setOption(self.radioButton.text())

    def eventFilter(self, source, event):
        if event.type() == QEvent.GraphicsSceneWheel and QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.zoomCanvas(event)
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
        self.graphicsView.scale(zoomFactor, zoomFactor)
        newPos = event.scenePos()
        delta = newPos - oldPos
        self.graphicsView.translate(delta.x(), delta.y())

