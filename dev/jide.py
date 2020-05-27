import json
from pathlib import Path
import shutil
import subprocess
import sys
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QAction, qApp, QUndoStack, QMessageBox, QTabWidget
from canvas import GraphicsScene, GraphicsView
from colorpalette import ColorPaletteDock
from colorpicker import downsample
from gamedata import GameData
from pixelpalette import PixelPaletteDock
from source import Source


class jide(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupWindow()
        self.setupTabs()
        self.setupDocks()
        self.setupActions()
        self.setupStatusBar()
        # DEMO
        self.openFile()
        # DEMO
        self.setCanvas(0)

    def setupWindow(self):
        self.setWindowTitle("JIDE")
        self.sprite_view = QGraphicsView()
        self.tile_view = QGraphicsView()
        self.sprite_view.setStyleSheet("background-color: #494949;")
        self.tile_view.setStyleSheet("background-color: #494949;")

    def setupDocks(self):
        self.sprite_color_palette_dock = ColorPaletteDock(Source.SPRITE, self)
        self.sprite_pixel_palette_dock = PixelPaletteDock(Source.SPRITE, self)
        self.tile_color_palette_dock = ColorPaletteDock(Source.TILE, self)
        self.tile_pixel_palette_dock = PixelPaletteDock(Source.TILE, self)

    def setupTabs(self):
        self.canvas_tabs = QTabWidget()
        self.canvas_tabs.addTab(self.sprite_view, "Sprites")
        self.canvas_tabs.addTab(self.tile_view, "Tiles")
        self.setCentralWidget(self.canvas_tabs)

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
        self.sprite_scene = GraphicsScene(self.data, Source.SPRITE, self)
        self.tile_scene = GraphicsScene(self.data, Source.TILE, self)
        self.sprite_view = GraphicsView(self.sprite_scene, self)
        self.tile_view = GraphicsView(self.tile_scene, self)
        self.sprite_view.setStyleSheet("background-color: #494949;")
        self.tile_view.setStyleSheet("background-color: #494949;")

        self.sprite_pixel_palette_dock.pixel_palette.subject_selected.connect(self.sprite_scene.setSubject)
        self.sprite_scene.set_color_switch_enabled.connect(self.sprite_color_palette_dock.color_palette.color_preview.setColorSwitchEnabled)
        self.sprite_color_palette_dock.palette_updated.connect(self.sprite_scene.setColorPalette)
        self.sprite_color_palette_dock.palette_updated.connect(self.sprite_pixel_palette_dock.palette_updated)
        self.sprite_color_palette_dock.color_palette.color_selected.connect(self.sprite_scene.setPrimaryColor)

        self.tile_pixel_palette_dock.pixel_palette.subject_selected.connect(self.tile_scene.setSubject)
        self.tile_scene.set_color_switch_enabled.connect(self.tile_color_palette_dock.color_palette.color_preview.setColorSwitchEnabled)
        self.tile_color_palette_dock.palette_updated.connect(self.tile_scene.setColorPalette)
        self.tile_color_palette_dock.palette_updated.connect(self.tile_pixel_palette_dock.palette_updated)
        self.tile_color_palette_dock.color_palette.color_selected.connect(self.tile_scene.setPrimaryColor)

        self.sprite_color_palette_dock.setup(self.data)
        self.tile_color_palette_dock.setup(self.data)
        self.sprite_pixel_palette_dock.setup(self.data)
        self.tile_pixel_palette_dock.setup(self.data)
        self.canvas_tabs = QTabWidget()
        self.canvas_tabs.addTab(self.sprite_view, "Sprites")
        self.canvas_tabs.addTab(self.tile_view, "Tiles")
        self.setCentralWidget(self.canvas_tabs)
        self.canvas_tabs.currentChanged.connect(self.setCanvas)
        self.setCanvas(0)

    @pyqtSlot(int)
    def setCanvas(self, index):
        try:
            self.paste_act.triggered.disconnect()
        except:
            pass
        try:
            self.copy_act.triggered.disconnect()
        except:
            pass

        if index == 0:
            self.copy_act.triggered.connect(self.sprite_scene.copy)
            self.paste_act.triggered.connect(self.sprite_scene.startPasting)
            self.tile_color_palette_dock.hide()
            self.tile_pixel_palette_dock.hide()
            self.sprite_color_palette_dock.show()
            self.sprite_pixel_palette_dock.show()
            self.removeDockWidget(self.tile_color_palette_dock)
            self.removeDockWidget(self.tile_pixel_palette_dock)
            self.addDockWidget(Qt.RightDockWidgetArea, self.sprite_color_palette_dock)
            self.addDockWidget(Qt.RightDockWidgetArea, self.sprite_pixel_palette_dock)
            self.copy_act.triggered.connect(self.sprite_scene.copy)
            self.paste_act.triggered.connect(self.sprite_scene.startPasting)
            self.sprite_scene.region_copied.connect(self.paste_act.setEnabled)
            self.sprite_scene.region_selected.connect(self.copy_act.setEnabled)
        elif index == 1:
            self.copy_act.triggered.connect(self.tile_scene.copy)
            self.paste_act.triggered.connect(self.tile_scene.startPasting)
            self.sprite_color_palette_dock.hide()
            self.sprite_pixel_palette_dock.hide()
            self.tile_color_palette_dock.show()
            self.tile_pixel_palette_dock.show()
            self.removeDockWidget(self.sprite_color_palette_dock)
            self.removeDockWidget(self.sprite_pixel_palette_dock)
            self.addDockWidget(Qt.RightDockWidgetArea, self.tile_color_palette_dock)
            self.addDockWidget(Qt.RightDockWidgetArea, self.tile_pixel_palette_dock)
            self.copy_act.triggered.connect(self.tile_scene.copy)
            self.paste_act.triggered.connect(self.tile_scene.startPasting)
            self.tile_scene.region_copied.connect(self.paste_act.setEnabled)
            self.tile_scene.region_selected.connect(self.copy_act.setEnabled)

    def genDATFiles(self):
        dir_path = Path(__file__).resolve().parent
        dat_path = dir_path / "DAT Files"
        dat_path.mkdir(exist_ok=True)
        tcp_path = dat_path / "tile_color_palettes.dat"
        tpp_path = dat_path / "tiles.dat"
        scp_path = dat_path / "sprite_color_palettes.dat"
        spp_path = dat_path / "sprites.dat"

        tile_pixel_data = self.data.getPixelPalettes(Source.TILE)
        tile_color_data = self.data.getColPals(Source.TILE)
        sprite_pixel_data = self.data.getPixelPalettes(Source.SPRITE)
        sprite_color_data = self.data.getColPals(Source.SPRITE)

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