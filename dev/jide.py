from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from colorpalette import *
from gamedata import GameData
import json
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup main window
        self.setWindowTitle("JIDE")

        # Setup color palette dock
        self.color_palette = ColorPalette()
        self.colorPaletteDock = QDockWidget("Color Palettes", self)
        self.testDock = QDockWidget("Test", self)
        self.colorPaletteDock.setWidget(self.color_palette)
        self.testDock.setWidget(QRadioButton("Test"))
        self.colorPaletteDock.setFloating(False)
        self.testDock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.testDock)

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
            try:
                self.data = GameData.from_filename(file_name)
            except KeyError:
                print("Malformed file")
            except OSError:
                print("Error opening file")
            else:
                # Setup canvas
                self.scene = GraphicsScene(self)
                self.view = GraphicsView(self.scene, self)
                self.setCentralWidget(self.view)
                self.view.setStyleSheet("background-color: #494949;")

                self.scene.setCanvas(self.data.sprite_pixel_palettes[80])
                self.scene.setPalette(self.data.sprite_color_palettes[2])
                self.scene.showSprite()

                # Setup color palette signals
                for swatch in self.color_palette.swatches:
                    swatch.clicked.connect(self.scene.changeColor)