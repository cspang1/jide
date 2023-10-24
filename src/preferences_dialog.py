from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog
)
from serial.tools import list_ports
from PyQt5.QtCore import pyqtSlot
from ui.preferences_dialog_ui import Ui_preferences_dialog

class PreferencesDialog(QDialog, Ui_preferences_dialog):
    def __init__(self, cpu_port, gpu_port, jcap_path, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.jcap_path_browse.clicked.connect(self.browse_to_jcap)

        com_ports = [
            port.__dict__["device"] for port in list(list_ports.comports())
        ]

        if len(com_ports) > 1:
            self.com_port_warning.setVisible(False)
            self.cpu_port_combo.addItems(com_ports)
            self.gpu_port_combo.addItems(com_ports)
            self.cpu_port_combo.setCurrentIndex(0)
            self.gpu_port_combo.setCurrentIndex(1)
            if cpu_port is not None and cpu_port in com_ports:
                self.cpu_port_combo.setCurrentText(cpu_port)
            if gpu_port is not None and gpu_port in com_ports:
                self.gpu_port_combo.setCurrentText(gpu_port)
            if jcap_path is not None:
                self.jcap_path_edit.setText(jcap_path)
        else:
            self.cpu_port_combo.setEnabled(False)
            self.gpu_port_combo.setEnabled(False)

    @pyqtSlot()
    def browse_to_jcap(self):
        jcap_path = QFileDialog.getExistingDirectory(
            self,
            "Select JCAP Directory",
            self.jcap_path_edit.text(),
            QFileDialog.ShowDirsOnly,
        )

        if dir:
            self.jcap_path_edit.setText(jcap_path)

    def get_cpu_port(self):
        return self.cpu_port_combo.currentText()

    def get_gpu_port(self):
        return self.gpu_port_combo.currentText()

    def get_jcap_path(self):
        return self.jcap_path_edit.text()
