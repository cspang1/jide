from PyQt5 import QtWidgets, uic
from canvas import GraphicsView
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(ui_path, "mainwindow.ui"), self)
        self.setWindowTitle("JIDE")
        self.setCentralWidget(self.canvas)
        self.setStyleSheet("background-color: #494949;")