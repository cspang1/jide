import json
from itertools import chain
from math import ceil
from pathlib import Path
import sys
from PyQt5.QtCore import QSize, QSettings
from PyQt5.QtGui import QPixmap, QKeySequence
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
from pixel_palette import PixelPalette
from color_palette import ColorPalette

class Window(QMainWindow, Ui_main_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_window()
        self.setup_actions()
        self.prefs = QSettings()

        QApplication.processEvents()

        self.load_project("./data/demo.jrf")
        self.test_scene()

    def setup_window(self):
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()
        self.map_color_palette_dock.hide()
        self.map_pixel_palette_dock.hide()

    def setup_actions(self):
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
        prefs_dialog = PreferencesDialog()
        prefs_dialog.exec()

    def load_project(self, file_name):
        if not file_name:
            return

        try:
            project_data = None
            with open(file_name, "r") as data_file:
                project_data =json.load(data_file)
            self.sprite_pixel_data = PixelData(project_data["sprites"])
            self.tile_pixel_data = PixelData(project_data["tiles"])
            self.sprite_color_data = ColorData(project_data["spriteColorPalettes"])
            self.tile_color_data = ColorData(project_data["tileColorPalettes"])
        except OSError:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to open project file",
            ).exec()
            return
        except KeyError:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to load project due to malformed data",
            ).exec()
            return
        
        self.enable_ui()

    def enable_ui(self):
        self.tool_bar.setEnabled(True)
        self.editor_tabs.setEnabled(True)
        for menu in self.menu_bar.findChildren(QMenu):
            for action in menu.actions():
                action.setEnabled(True)
        for dock in self.findChildren(ColorPalette):
            dock.setEnabled(True)
        for dock in self.findChildren(PixelPalette):
            dock.setEnabled(True)

    def test_scene(self):
        self.sprite_scene = QGraphicsScene()
        self.tile_scene = QGraphicsScene()
        self.tile_pixel_data.setColorTable(
            [color.rgba() for color in self.tile_color_data.color_table("tile_color_palette0")]
            )
        self.sprite_pixel_data.setColorTable(
            [color.rgba() for color in self.sprite_color_data.color_table("sprite_color_palette0")]
            )
        sprite_pixmap = QPixmap.fromImage(self.sprite_pixel_data) 
        tile_pixmap = QPixmap.fromImage(self.tile_pixel_data) 
        self.sprite_scene.addPixmap(sprite_pixmap)
        self.tile_scene.addPixmap(tile_pixmap)
        self.sprite_editor_view.setScene(self.sprite_scene)
        self.tile_editor_view.setScene(self.tile_scene)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())