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


class Window(QMainWindow, Ui_main_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_actions()
        self.tile_color_palette_dock.hide()
        self.tile_pixel_palette_dock.hide()

        QApplication.processEvents()

        self.test_scene()
        self.sprite_pixel_data = None
        self.tile_pixel_data = None
        self.load_project("./data/demo.jrf")

    def test_scene(self):
        self.scene = QGraphicsScene()
        pixmap = QPixmap("E:\JCAP\jide\\ref\jcap.png")
        self.scene.addPixmap(pixmap)
        self.sprite_editor_view.setScene(self.scene)

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

        project_data = None
        sprite_pixel_json = None
        tile_pixel_json = None

        try:
            with open(file_name, "r") as data_file:
                project_data =json.load(data_file)
        except OSError:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to open project file",
            ).exec()
            return
        
        try:
            sprite_pixel_json = project_data["sprites"]
            tile_pixel_json = project_data["tiles"]

            for sprite in sprite_pixel_json:
                pass
        except KeyError:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "Unable to load project due to malformed data",
            ).exec()
            return

        self.sprite_pixel_palette = PixelData(sprite_pixel_json)
        self.tile_pixel_palette = PixelData(tile_pixel_json)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())