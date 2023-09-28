import json
from math import ceil
from pathlib import Path
import sys
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsScene, QMessageBox
)

from ui.main_window_ui import Ui_main_window
from preferences_dialog import PreferencesDialog
from pixel_data import PixelData
from color_data import ColorData

class Window(QMainWindow, Ui_main_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_actions()
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()

        QApplication.processEvents()

        self.sprite_pixel_data = None
        self.tile_pixel_data = None
        self.sprite_color_data = None
        self.tile_color_data = None

        self.load_project("./data/demo.jrf")
        self.test_scene()

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

    def setup_actions(self):
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
        self.editor_tabs.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())