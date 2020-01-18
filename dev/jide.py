from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from colorpalette import *
from pixelpalette import *
from gamedata import GameData
from sources import Sources
from pathlib import Path
import json
import sys

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
        self.colorPaletteDock = ColorPaletteDock(self)
        self.pixelPaletteDock = PixelPaletteDock(Sources.SPRITE, self)
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
        undo_act = self.undo_stack.createUndoAction(self, "&Undo")
        undo_act.setShortcut(QKeySequence.Undo)
        redo_act = self.undo_stack.createRedoAction(self, "&Redo")
        redo_act.setShortcut(QKeySequence.Redo)

        # JCAP compile/load
        self.gendat_act = QAction("&Generate DAT Files", self)
        self.gendat_act.setShortcut("Ctrl+D")
        self.gendat_act.setStatusTip("Generate DAT Files")
        self.gendat_act.triggered.connect(self.genDATFiles)
        self.gendat_act.setEnabled(False)

        # Build menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(open_file)
        file_menu.addAction(exit_act)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)
        jcap_menu = menu_bar.addMenu("&JCAP")
        jcap_menu.addAction(self.gendat_act)

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
        self.gendat_act.setEnabled(True)
        self.data.setUndoStack(self.undo_stack)
        self.scene = GraphicsScene(self.data, Sources.SPRITE, self)
        self.pixelPaletteDock.pixel_palette.subject_selected.connect(self.scene.setSubject)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")
        self.colorPaletteDock.palette_updated.connect(self.scene.setPalette)
        self.colorPaletteDock.color_palette.color_selected.connect(self.scene.setPenColor)
        self.colorPaletteDock.setup(self.data)
        self.pixelPaletteDock.setup(self.data)

    def genDATFiles(self):
        dir_path = Path(__file__).resolve().parent
        dat_path = dir_path / "DAT Files"
        dat_path.mkdir(exist_ok=True)
        tcp_path = dat_path / "tile_color_palettes.dat"
        tpp_path = dat_path / "tiles.dat"
        scp_path = dat_path / "sprite_color_palettes.dat"
        spp_path = dat_path / "sprites.dat"

        tile_pixel_data = self.data.getTiles()
        tile_color_data = self.data.getTileColPals()
        sprite_pixel_data = self.data.getSprites()
        sprite_color_data = self.data.getSprColPals()

        self.genPixelDATFile(tile_pixel_data, tpp_path)
        self.genColorDATFile(tile_color_data, tcp_path)
        self.genPixelDATFile(sprite_pixel_data, spp_path)
        self.genColorDATFile(sprite_color_data, scp_path)

    def genPixelDATFile(self, source, path):
        with path.open("wb") as dat_file:
            for element in source:
                for line in element:
                    total = 0
                    for pixel in line:
                        total = (total << 4) + pixel
                    dat_file.write(total.to_bytes(4, byteorder="big")[::-1])

    def genColorDATFile(self, source, path):
        with path.open("wb") as dat_file:
            for palette in source:
                for color in palette:
                    r, g, b = downsample(color.red(), color.green(), color.blue())
                    rgb = (r << 5)|(g << 2)|(b)
                    dat_file.write(bytes([rgb]))