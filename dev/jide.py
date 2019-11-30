from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from colorpalette import *
import json
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup main window
        self.setWindowTitle("JIDE")

        # Setup canvas
        self.scene = GraphicsScene(self)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")

        # Setup color palette dock
        self.colorPaletteDock = QDockWidget("Color Palettes", self)
        self.color_palette = ColorPalette()
        self.colorPaletteDock.setWidget(self.color_palette)
        self.colorPaletteDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)
        self.color_palette.setStyleSheet("background-color: #494949;")

        # Setup color palette signals
        for swatch in self.color_palette.swatches:
            swatch.clicked.connect(self.scene.changeColor)

        # Setup menu bar
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        openFile = QAction('&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open file')
        openFile.triggered.connect(self.openFile)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(openFile)

    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JCAP Resource File (*.jrf)")

        if file_name:
            with open(file_name, 'r') as f:
                self.data = json.load(f)
                for sprite in self.data["sprites"]:
                    print(sprite["name"])