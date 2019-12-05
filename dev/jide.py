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
        self.view = QGraphicsView()
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")

        # Setup color palette dock
        self.colorPaletteDock = QDockWidget("Color Palettes", self)
        self.colorPaletteDock.setFloating(False)
        self.dockedWidget = QWidget(self)
        self.colorPaletteDock.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(QGridLayout())

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
                self.scene = GraphicsScene( self.data, self)
                self.view = GraphicsView(self.scene, self)
                self.setCentralWidget(self.view)
                self.view.setStyleSheet("background-color: #494949;")
                self.scene.setCanvas("sprite80")
                self.scene.showSprite()

                # Setup color palette
                self.color_palette = ColorPalette(self.data)
                self.color_palette_list = QComboBox()
                self.color_palette_list.setEnabled(False)
                self.color_palette_list.currentIndexChanged.connect(self.setColorPalette)
                self.dockedWidget.layout().addWidget(self.color_palette_list)
                self.dockedWidget.layout().addWidget(self.color_palette)
                self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)
                self.color_palette_list.setEnabled(True)
                for palette in self.data.sprite_color_palettes:
                    self.color_palette_list.addItem(palette)

    def setColorPalette(self, index):
        item_name = self.color_palette_list.currentText()
        self.color_palette.setPalette(item_name)
        # This should happen w/ a signal probably...
        self.scene.setPalette(item_name)
