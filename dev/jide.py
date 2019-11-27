from PyQt5 import QtWidgets, uic
from canvas import GraphicsView
from PyQt5 import QtCore
from colorpalette import *
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(ui_path, "mainwindow.ui"), self)
        self.setWindowTitle("JIDE")
        self.setStyleSheet("background-color: #494949;")

        # Setup canvas
        self.setCentralWidget(self.canvas)

        # Setup color palette
        color_palette = ColorPalette()
        for swatch in color_palette.swatches:
            swatch.clicked.connect(self.canvas.scene.changeColor)
        self.colorPalette.setWidget(color_palette)
