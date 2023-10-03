import json
from itertools import chain
from math import ceil, floor
from pathlib import Path
import sys
from PyQt5.QtCore import QSize, QSettings, QCoreApplication, pyqtSlot
from PyQt5.QtGui import QPixmap, QKeySequence, QColor, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QGraphicsScene,
    QMessageBox,
    QActionGroup,
    QUndoStack,
    QMenu,
    QDockWidget
)

from ui.main_window_ui import Ui_main_window
from preferences_dialog import PreferencesDialog
from pixel_data import PixelData
from color_data import ColorData
from color_data import upsample, downsample
from pixel_palette import PixelPalette
from color_palette import ColorPalette

class Jide(QMainWindow, Ui_main_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_window()
        self.prefs = QSettings()
        QCoreApplication.setOrganizationName("Connor Spangler")
        QCoreApplication.setOrganizationDomain("https://github.com/cspang1")
        QCoreApplication.setApplicationName("JIDE")
        QApplication.processEvents()

        self.load_project("./data/demo.jrf")
        self.test_scene()

    def setup_window(self):
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()
        self.map_color_palette_dock.hide()
        self.map_pixel_palette_dock.hide()

        self.tool_actions = QActionGroup(self)
        self.tool_actions.addAction(self.action_select_tool)
        self.tool_actions.addAction(self.action_pen_tool)
        self.tool_actions.addAction(self.action_fill_tool)
        self.tool_actions.addAction(self.action_line_tool)
        self.tool_actions.addAction(self.action_rectangle_tool)
        self.tool_actions.addAction(self.action_ellipse_tool)

        self.undo_stack = QUndoStack(self)
        action_undo = self.undo_stack.createUndoAction(self, "&Undo")
        action_undo.setShortcut(QKeySequence.Undo)
        action_redo = self.undo_stack.createRedoAction(self, "&Redo")
        action_redo.setShortcut(QKeySequence.Redo)
        self.menu_edit.addActions([action_undo, action_redo])

        self.action_new.triggered.connect(lambda temp: print("this will create a new project"))
        self.action_save.triggered.connect(lambda temp: print("this will save the current project"))
        self.action_copy.triggered.connect(lambda temp: print("this will copy the current selection"))
        self.action_paste.triggered.connect(lambda temp: print("this will paste the current selection"))
        self.action_gen_dat_files.triggered.connect(lambda temp: print("this will generate .DAT files"))
        self.action_load_jcap_system.triggered.connect(lambda temp: print("this will load the JCAP system"))
        self.action_open.triggered.connect(self.select_file)
        self.action_exit.triggered.connect(self.close)
        self.action_preferences.triggered.connect(self.open_preferences)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            str(Path(__file__)),
            "JCAP Resource File (*.jrf)",
        )
        self.load_project(file_name)

    def open_preferences(self):
        prefs = QSettings()
        cpu_port = None
        gpu_port = None
        jcap_path = None
        prefs.beginGroup("ports")
        if prefs.contains("cpu_port"):
            cpu_port = prefs.value("cpu_port")
        if prefs.contains("gpu_port"):
            gpu_port = prefs.value("gpu_port")
        prefs.endGroup()
        prefs.beginGroup("paths")
        if prefs.contains("jcap_path"):
            jcap_path = prefs.value("jcap_path")
        prefs.endGroup()

        prefs_dialog = PreferencesDialog(cpu_port, gpu_port, jcap_path)
        valid_prefs = False
        while not valid_prefs:
            if prefs_dialog.exec():
                cpu_port = prefs_dialog.get_cpu_port()
                gpu_port = prefs_dialog.get_gpu_port()
                jcap_path = prefs_dialog.get_jcap_path()
            if cpu_port and gpu_port and cpu_port == gpu_port:
                self.show_error_dialog("CPU and GPU COM ports must be different")
            else:
                valid_prefs = True

        prefs.beginGroup("ports")
        prefs.setValue("cpu_port", cpu_port)
        prefs.setValue("gpu_port", gpu_port)
        prefs.endGroup()
        prefs.beginGroup("paths")
        prefs.setValue("jcap_path", jcap_path)
        prefs.endGroup()

    def load_project(self, file_name):
        if not file_name:
            return

        try:
            project_data = None
            with open(file_name, "r") as data_file:
                project_data =json.load(data_file)
            self.setup_models(project_data)

        except OSError:
            self.show_error_dialog("Unable to open project file")
            return
        except KeyError:
            self.show_error_dialog("Unable to load project due to malformed data")
            return
        
        self.init_ui()

    def setup_models(self, project_data):
        self.sprite_color_data = ColorData()
        self.tile_color_data = ColorData()

        self.sprite_color_data.error_thrown.connect(self.show_error_dialog)
        self.tile_color_data.error_thrown.connect(self.show_error_dialog)

        self.sprite_color_palette.color_palette_name_combo.currentIndexChanged.connect(
            lambda: self.sprite_color_palette.change_palette(
                self.sprite_color_data.get_color_palette(
                    self.sprite_color_palette.color_palette_name_combo.currentText()
                )
            )
        )
        self.tile_color_palette.color_palette_name_combo.currentIndexChanged.connect(
            lambda: self.tile_color_palette.change_palette(
                self.tile_color_data.get_color_palette(
                    self.tile_color_palette.color_palette_name_combo.currentText()
                )
            )
        )
        self.sprite_color_data.color_palette_added.connect(self.sprite_color_palette.add_color_palette)
        self.sprite_color_data.color_palette_removed.connect(self.sprite_color_palette.remove_color_palette)
        self.tile_color_data.color_palette_added.connect(self.tile_color_palette.add_color_palette)
        self.tile_color_data.color_palette_removed.connect(self.tile_color_palette.remove_color_palette)
        self.sprite_color_data.color_palette_renamed.connect(self.sprite_color_palette.rename_color_palette)
        self.sprite_color_palette.color_changed.connect(
            lambda color, index: self.sprite_color_data.update_color(
                self.sprite_color_palette.color_palette_name_combo.currentText(),
                color,
                index
            )
        )
        self.tile_color_palette.color_changed.connect(
            lambda color, index: self.tile_color_data.update_color(
                self.tile_color_palette.color_palette_name_combo.currentText(),
                color,
                index
            )
        )
        self.sprite_color_data.color_updated.connect(
            lambda _, color, index:  self.sprite_color_palette.update_color(color, index)
        )
        self.tile_color_data.color_updated.connect(
            lambda _, color, index:  self.tile_color_palette.update_color(color, index)
        )
        self.sprite_color_palette.color_palette_added.connect(
            lambda name: self.sprite_color_data.add_color_palette(name, [QColor(255, 0, 255)] * 16)
        )
        self.tile_color_palette.color_palette_added.connect(
            lambda name: self.tile_color_data.add_color_palette(name, [QColor(255, 0, 255)] * 16)
        )
        self.sprite_color_palette.color_palette_renamed.connect(self.sprite_color_data.rename_color_palette)
        self.sprite_color_palette.color_palette_removed.connect(self.sprite_color_data.remove_color_palette)
        self.tile_color_palette.color_palette_removed.connect(self.tile_color_data.remove_color_palette)
        for palette in parse_color_data(project_data["spriteColorPalettes"]):
            self.sprite_color_data.add_color_palette(*palette)
        for palette in parse_color_data(project_data["tileColorPalettes"]):
            self.tile_color_data.add_color_palette(*palette)

        self.sprite_pixel_data = PixelData(*parse_pixel_data(project_data["sprites"]))
        self.tile_pixel_data = PixelData(*parse_pixel_data(project_data["tiles"]))

    def init_ui(self):
        self.tool_bar.setEnabled(True)
        self.editor_tabs.setEnabled(True)
        for menu in self.menu_bar.findChildren(QMenu):
            for action in menu.actions():
                action.setEnabled(True)
        for palette in self.findChildren(ColorPalette):
            palette.setEnabled(True)
        for palette in self.findChildren(PixelPalette):
            palette.setEnabled(True)

    def test_scene(self):
        self.sprite_scene = QGraphicsScene()
        self.tile_scene = QGraphicsScene()
        self.tile_pixel_data.setColorTable(
            [color.rgba() for color in self.tile_color_data.get_color_palette("tile_color_palette0")]
            )
        self.sprite_pixel_data.setColorTable(
            [color.rgba() for color in self.sprite_color_data.get_color_palette("sprite_color_palette0")]
            )
        sprite_pixmap = QPixmap.fromImage(self.sprite_pixel_data) 
        tile_pixmap = QPixmap.fromImage(self.tile_pixel_data) 
        self.sprite_scene.addPixmap(sprite_pixmap)
        self.tile_scene.addPixmap(tile_pixmap)
        self.sprite_editor_view.setScene(self.sprite_scene)
        self.tile_editor_view.setScene(self.tile_scene)

    @pyqtSlot(str)
    def show_error_dialog(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()

def parse_pixel_data(data):
    pixels_per_element = 64
    element_width = 8
    element_height = 8
    elements_per_line = 16
    pixel_data = bytearray([0] * len(data) * pixels_per_element)
    names = []

    for index, palette in enumerate(data):
        names.append(palette["name"])
        col_index = floor(index / elements_per_line) * element_width * elements_per_line * element_height
        col_offset = (index % elements_per_line) * element_width
        for pixel_row, pixel_row_data in enumerate(palette["contents"]):
            row_offset = pixel_row * elements_per_line * element_width
            pixel_data_index = col_index + row_offset + col_offset
            pixel_data[pixel_data_index:pixel_data_index+8] = pixel_row_data

    width = element_width * elements_per_line
    height = ceil(len(pixel_data) / width)
    return (pixel_data, width, height, names)

def parse_color_data(data):
    for palette in data:
        cur_pal = palette["contents"]
        cur_pal[:] = [
            QColor(*upsample(color >> 5, (color >> 2) & 7, color & 3))
            for color in cur_pal
        ]
        yield (palette["name"], cur_pal)