from pathlib import Path
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog
)

from main_window_ui import Ui_main_window
from preferences_dialog import PreferencesDialog

class Window(QMainWindow, Ui_main_window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setup_actions()

    def setup_actions(self):
        self.action_open.triggered.connect(self.selectFile)
        self.action_exit.triggered.connect(self.close)
        self.action_preferences.triggered.connect(self.open_preferences)

    def selectFile(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            str(Path(__file__)),
            "JCAP Resource File (*.jrf)",
        )
        self.loadProject(file_name)

    def open_preferences(self):
        prefs_dialog = PreferencesDialog()
        prefs_dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())