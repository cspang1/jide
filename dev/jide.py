from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from colorpalette import *
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup main window
        self.setWindowTitle("JIDE")
        self.setStyleSheet("background-color: #494949;")

        # Setup canvas
        self.scene = GraphicsScene(self)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Setup color palette dock
        self.colorPaletteDock = QDockWidget("Color Palettes", self)
        self.color_palette = ColorPalette()
        self.colorPaletteDock.setWidget(self.color_palette)
        self.colorPaletteDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)

        # Setup color palette signals
        for swatch in self.color_palette.swatches:
            swatch.clicked.connect(self.scene.changeColor)
