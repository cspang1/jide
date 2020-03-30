from PyQt5 import QtWidgets, uic
from canvas import *
from PyQt5 import QtCore
from PyQt5.Qt import QApplication, QClipboard
from colorpalette import *
from pixelpalette import *
from gamedata import GameData
from sources import Sources
from pathlib import Path
import json
import sys
import shutil
import subprocess

class jide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupWindow()
        self.setupDocks()
        self.setupActions()
        self.setupStatusBar()
        # DEMO
        self.openFile()
        # DEMO

    def setupWindow(self):
        self.setWindowTitle("JIDE")
        self.view = QGraphicsView()
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")

    def setupDocks(self):
        self.colorPaletteDock = ColorPaletteDock(self)
        self.pixelPaletteDock = PixelPaletteDock(Sources.SPRITE, self)
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
        # DEMO
        open_file.setEnabled(False)
        # DEMO

        # Undo/redo
        self.undo_stack = QUndoStack(self)
        undo_act = self.undo_stack.createUndoAction(self, "&Undo")
        undo_act.setShortcut(QKeySequence.Undo)
        redo_act = self.undo_stack.createRedoAction(self, "&Redo")
        redo_act.setShortcut(QKeySequence.Redo)

        # Copy/paste
        self.copy_act = QAction("&Copy", self)
        self.copy_act.setShortcut("Ctrl+C")
        self.copy_act.setStatusTip("Copy")
        self.copy_act.setEnabled(False)
        self.paste_act = QAction("&Paste", self)
        self.paste_act.setShortcut("Ctrl+V")
        self.paste_act.setStatusTip("Paste")
        self.paste_act.setEnabled(False)

        # JCAP compile/load
        self.gendat_act = QAction("&Generate DAT Files", self)
        self.gendat_act.setShortcut("Ctrl+D")
        self.gendat_act.setStatusTip("Generate DAT Files")
        self.gendat_act.triggered.connect(self.genDATFiles)
        self.gendat_act.setEnabled(False)
        self.load_jcap = QAction("&Load JCAP System", self)
        self.load_jcap.setShortcut("Ctrl+L")
        self.load_jcap.setStatusTip("Load JCAP System")
        self.load_jcap.setEnabled(False)
        self.load_jcap.triggered.connect(self.loadJCAP)

        # Build menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(open_file)
        file_menu.addAction(exit_act)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(undo_act)
        edit_menu.addAction(redo_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)
        jcap_menu = menu_bar.addMenu("&JCAP")
        jcap_menu.addAction(self.gendat_act)
        jcap_menu.addAction(self.load_jcap)

    def setupStatusBar(self):
        self.statusBar = self.statusBar()

    @pyqtSlot(bool)
    def setCopyActive(self, active):
        self.copy_act.isEnabled(active)

    @pyqtSlot(bool)
    def setPasteActive(self, active):
        self.paste_act.isEnabled(active)

    def openFile(self):
        # DEMO
        #file_name, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JCAP Resource File (*.jrf)")
        dir_path = Path(__file__).resolve().parent
        file_name = dir_path / "demo.jrf"
        #DEMO
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
        self.load_jcap.setEnabled(True)
        self.data.setUndoStack(self.undo_stack)
        self.scene = GraphicsScene(self.data, Sources.SPRITE, self)
        self.pixelPaletteDock.pixel_palette.subject_selected.connect(self.scene.setSubject)
        self.view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setStyleSheet("background-color: #494949;")
        self.colorPaletteDock.palette_updated.connect(self.scene.setColorPalette)
        self.colorPaletteDock.palette_updated.connect(self.pixelPaletteDock.palette_updated)
        self.colorPaletteDock.color_palette.color_selected.connect(self.scene.setPrimaryColor)
        self.colorPaletteDock.setup(self.data)
        self.pixelPaletteDock.setup(self.data)
        self.copy_act.triggered.connect(self.scene.copy)
        self.paste_act.triggered.connect(self.scene.paste)
        self.scene.region_selected.connect(self.copy_act.setEnabled)
        self.scene.region_copied.connect(self.paste_act.setEnabled)

    def genDATFiles(self):
        dir_path = Path(__file__).resolve().parent
        dat_path = dir_path / "DAT Files"
        dat_path.mkdir(exist_ok=True)
        #tcp_path = dat_path / "tile_color_palettes.dat"
        #tpp_path = dat_path / "tiles.dat"
        scp_path = dat_path / "sprite_color_palettes.dat"
        spp_path = dat_path / "sprites.dat"

        #tile_pixel_data = self.data.getTiles()
        #tile_color_data = self.data.getTileColPals()
        sprite_pixel_data = self.data.getSprites()
        sprite_color_data = self.data.getSprColPals()

        #self.genPixelDATFile(tile_pixel_data, tpp_path)
        #self.genColorDATFile(tile_color_data, tcp_path)
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

    def loadJCAP(self):
        self.statusBar.showMessage("Loading JCAP...")
        self.genDATFiles()
        dir_path = Path(__file__).resolve().parent
        dat_path = dir_path / "DAT Files"
        tcp_path = dat_path / "tile_color_palettes.dat"
        tpp_path = dat_path / "tiles.dat"
        scp_path = dat_path / "sprite_color_palettes.dat"
        spp_path = dat_path / "sprites.dat"
        jcap_path = Path(__file__).parents[2] / "jcap" / "dev" / "software"
        sysload_path = jcap_path / "sysload.sh"

        for dat_file in dat_path.glob("**/*"):
            shutil.copy(str(dat_file), str(jcap_path))
        
        result = subprocess.run(["bash.exe", str(sysload_path), "-c", "COM3", "-g", "COM4"], capture_output=True)
        print(result.stdout)
        print(result.stderr)
        self.statusBar.showMessage("JCAP Loaded!", 5000)