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

        self.setupWindow()
        self.setupDocks()
        self.setupMenuBar()
        self.setupStatusBar()

    def setupWindow(self):
        self.setWindowTitle("JIDE")
        self.view = QGraphicsView()
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")

    def setupDocks(self):
        self.colorPaletteDock = ColorPaletteDock("Color Palettes", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)

    def setupMenuBar(self):
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        openFile = QAction('&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open file')
        openFile.triggered.connect(self.openFile)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(openFile)

    def setupStatusBar(self):
        self.statusBar()

    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JCAP Resource File (*.jrf)")
        if file_name:
            try:
                self.data = GameData.from_filename(file_name)
            except KeyError:
                QMessageBox(QMessageBox.Critical, "Error", "Unable to load project due to malformed data").exec()
            except OSError:
                QMessageBox(QMessageBox.Critical, "Error", "Unable to open project file").exec()
            else:
                self.loadProject()

    def loadProject(self):
        self.scene = GraphicsScene(self.data, self)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")
        self.scene.setSprite("sprite80")
        self.colorPaletteDock.palette_updated.connect(self.scene.setPalette)
        for swatch in self.colorPaletteDock.color_palette.palette:
            swatch.pen_changed.connect(self.scene.setPenColor)
        self.colorPaletteDock.setup(self.data)