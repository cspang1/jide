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
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)
        self.dockedWidget = QWidget(self)
        self.colorPaletteDock.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(QGridLayout())

        # Setup color palette
        self.color_palette = ColorPalette()
        self.color_palette_list = QComboBox()
        self.color_palette_list.setEnabled(False)
        self.color_palette_list.currentIndexChanged.connect(self.setColorPalette)
        self.dockedWidget.layout().addWidget(self.color_palette_list)
        self.dockedWidget.layout().addWidget(self.color_palette)

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
                self.scene.setCanvas(self.data.sprite_pixel_palettes["sprite80"])
                self.scene.showSprite()

                # Setup color palette
                self.color_palette_list.setEnabled(True)
                for palette in self.data.sprite_color_palettes:
                    self.color_palette_list.addItem(palette)

                self.scene.draw_pixel.connect(self.data.update_pixel)
                self.data.data_changed.connect(self.scene.update_pixel)

    def setColorPalette(self, index):
        item_name = self.color_palette_list.currentText()
        palette = self.data.sprite_color_palettes[item_name]
        colors = [(color.red(), color.green(), color.blue()) for color in palette]
        self.color_palette.setPalette(colors)
        self.scene.setPalette(palette)
