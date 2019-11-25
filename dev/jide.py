from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPalette, QColor, QIcon, QPen, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QEvent
import sys
import os

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 1000, 1000)
        self.opt = ""

    def setOption(self, opt):
        self.opt = opt

    def mousePressEvent(self, event):
        pen = QPen(Qt.black)
        brush = QBrush(Qt.black)
        x = event.scenePos().x()
        y = event.scenePos().y()
        if self.opt == "Generate":
            self.addRect(x, y, 4, 4, pen, brush)
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
        print("{0}, {1}".format(event.scenePos().x(), event.scenePos().y()))
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        # Save the scene pos
        oldPos = event.scenePos()
        # Zoom
        if event.delta() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.graphicsView.scale(zoomFactor, zoomFactor)
        # Get the new position
        newPos = event.scenePos()
        # Move scene to old position
        delta = newPos - oldPos
        self.graphicsView.translate(delta.x(), delta.y())

