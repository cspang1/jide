from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QPalette, QColor, QIcon, QPen, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
import sys
import os

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(-100, -100, 200, 200)
        self.opt = ""

    def setOption(self, opt):
        self.opt = opt

    def mousePressEvent(self, event):
        pen = QPen(Qt.black)
        brush = QBrush(Qt.black)
        x = event.scenePos().x()
        y = event.scenePos().y()
        if self.opt == "Generate":
            self.addEllipse(x, y, 4, 4, pen, brush)
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
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)


        group = QButtonGroup(self)
        group.addButton(self.radioButton)
        group.addButton(self.radioButton_2)

        group.buttonClicked.connect(lambda btn: self.scene.setOption(btn.text()))
        self.radioButton.setChecked(True)
        self.scene.setOption(self.radioButton.text())

    def wheelEvent(self, event):
        if event.angleDelta().y() < 0:
            print("Zooming out: {0}".format(event.angleDelta().y()))
            self.graphicsView.scale(1/1.2, 1/1.2)
        else:
            print("Zooming in: {0}".format(event.angleDelta().y()))
            self.graphicsView.scale(1.2, 1.2)
