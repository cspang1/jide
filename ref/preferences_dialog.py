from PyQt5.QtWidgets import (
    QDialog
)

from ui.preferences_dialog_ui import Ui_preferences_dialog

class PreferencesDialog(QDialog, Ui_preferences_dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
