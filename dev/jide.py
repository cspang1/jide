from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from colorpalette import *
from pixelpalette import *
from gamedata import GameData
import json
import sys
import os

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupWindow()
        self.setupDocks()
        self.setupActions()
        self.setupStatusBar()

    def setupWindow(self):
        self.setWindowTitle("JIDE")
        self.view = QGraphicsView()
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")

    def setupDocks(self):
        self.colorPaletteDock = ColorPaletteDock("Color Palettes", self)
        self.pixelPaletteDock = PixelPaletteDock("Sprite Palettes", self)
        self.colorPaletteDock.palette_updated.connect(self.pixelPaletteDock.palette_updated)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorPaletteDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.pixelPaletteDock)

    def setupActions(self):
        # Exit
        exit_act = QAction("&Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.setStatusTip("Exit application")
        exit_act.triggered.connect(qApp.quit)

        # Open file
        open_file = QAction("&Open", self)
        open_file.setShortcut("Ctrl+O")
        open_file.setStatusTip("Open file")
        open_file.triggered.connect(self.openFile)

        # Undo/redo
        self.undo_stack = QUndoStack(self)
        undo_action = self.undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.Undo)
        redo_action = self.undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.Redo)

        # Build menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(open_file)
        file_menu.addAction(exit_act)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

    def setupStatusBar(self):
        self.statusBar()

    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JCAP Resource File (*.jrf)")
        if file_name:
            try:
                self.data = GameData.fromFilename(file_name, self)
            except KeyError:
                QMessageBox(QMessageBox.Critical, "Error", "Unable to load project due to malformed data").exec()
            except OSError:
                QMessageBox(QMessageBox.Critical, "Error", "Unable to open project file").exec()
            else:
                self.loadProject()

    def loadProject(self):
        self.data.setUndoStack(self.undo_stack)
        self.scene = GraphicsScene(self.data, self)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")
        self.scene.setSprite("sprite80")
        self.colorPaletteDock.palette_updated.connect(self.scene.setPalette)
        for swatch in self.colorPaletteDock.color_palette.palette:
            swatch.pen_changed.connect(self.scene.setPenColor)
        self.colorPaletteDock.setup(self.data)
        self.pixelPaletteDock.setup(self.data)