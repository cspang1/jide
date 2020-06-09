from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox


class Preferences(QDialog):
    """Represents the dialog containg the application settings

    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        actions = QDialogButtonBox(
            QDialogButtonBox.Ok
            |
            # QDialogButtonBox.Apply |
            QDialogButtonBox.Cancel
        )
        actions.accepted.connect(self.accept)
        actions.rejected.connect(self.reject)

        settings_form = QFormLayout()
        settings_form.addWidget(actions)
        self.setLayout(settings_form)
