import re
import subprocess
import time
from serial import serial_for_url
from serial.tools import list_ports
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import QSettings


class Preferences(QDialog):
    """Represents the dialog containg the application settings

    :param parent:  Parent widget, defaults to None
    :type parent:   QWidget, optional
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.prefs = QSettings()

        self.actions = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Cancel
        )
        self.actions.clicked.connect(self.handlePrefsBtns)
        settings_form = QFormLayout()

        com_ports = [
            port.__dict__["device"] for port in list(list_ports.comports())
        ]
        self.cpu_port_combo_box = QComboBox()
        self.cpu_port_combo_box.addItems(com_ports)
        self.gpu_port_combo_box = QComboBox()
        self.gpu_port_combo_box.addItems(com_ports)
        self.prefs.beginGroup("ports")
        if self.prefs.contains("cpu_port"):
            self.cpu_port_combo_box.setCurrentText(
                self.prefs.value("cpu_port")
            )
        if self.prefs.contains("gpu_port"):
            self.gpu_port_combo_box.setCurrentText(
                self.prefs.value("gpu_port")
            )
        self.prefs.endGroup()

        auto_ident = QPushButton("Auto-Identify CPU/GPU")
        auto_ident.clicked.connect(self.idUcs)
        settings_form.addRow(QLabel("Propeller Ports"))
        settings_form.addRow("CPU Port:", self.cpu_port_combo_box)
        settings_form.addRow("GPU Port:", self.gpu_port_combo_box)
        settings_form.addRow(auto_ident)

        jcap_path_prefs = QHBoxLayout()
        self.jcap_path = QLineEdit()
        self.prefs.beginGroup("paths")
        if self.prefs.contains("jcap_path"):
            self.jcap_path.setText(self.prefs.value("jcap_path"))
        self.prefs.endGroup()
        self.jcap_browse = QPushButton("Browse")
        self.jcap_browse.clicked.connect(self.browseToJcap)
        jcap_path_prefs.addWidget(QLabel("JCAP Path:"))
        jcap_path_prefs.addWidget(self.jcap_path)
        jcap_path_prefs.addWidget(self.jcap_browse)
        settings_form.addRow(jcap_path_prefs)

        settings_form.addRow(self.actions)
        self.setLayout(settings_form)

    def browseToJcap(self):
        dir = QFileDialog.getExistingDirectory(
            self,
            "Select JCAP Directory",
            self.jcap_path.text(),
            QFileDialog.ShowDirsOnly,
        )

        if dir:
            self.jcap_path.setText(dir)

    def idUcs(self):
        """Executes the serial routines necessary to identify which COM ports
        the GPU and CPU are on
        """
        new_cpu_port = None
        new_gpu_port = None
        for port in list(list_ports.comports()):
            result = subprocess.getoutput(
                [
                    "propellent.exe",
                    "/id",
                    "/port",
                    port.__dict__["device"],
                    "/gui",
                    "off",
                ]
            )
            prop_ports = re.search(
                r"Propeller chip version 1 found on (COM[0-9]+)", result
            )

            if prop_ports:
                port = prop_ports.group(1)
                ser = serial_for_url(port, 19200, timeout=0, do_not_open=True)
                ser.open()
                response = None
                start = time.time()
                timeout = 5
                while not response and time.time() < start + timeout:
                    ser.write(b"\x59")
                    response = ser.read(3)
                ser.close()
                if response == b"CPU":
                    new_cpu_port = port
                elif response == b"GPU":
                    new_gpu_port = port

        message = ""
        error = False
        if not new_cpu_port:
            message = (
                "CPU not detected on any COM port.\nPlease ensure that "
                "the debug switch is enabled and that the CPU serial "
                "plug is properly connected.\n\n"
            )
            error = True

        if not new_gpu_port:
            message += (
                "GPU not detected on any COM port.\nPlease ensure "
                "that the debug switch is enabled and that the GPU "
                "serial plug is properly connected.\n\n"
            )
            error = True

        if error:
            QMessageBox(QMessageBox.Critical, "Error", message).exec()
            return

        self.cpu_port_combo_box.setCurrentText(new_cpu_port)
        self.gpu_port_combo_box.setCurrentText(new_gpu_port)

    def handlePrefsBtns(self, button):
        """Handles Ok/Apply/Cancel preferences buttons

        :param button: Button which triggered the actions
        :type button: QPushButton
        """
        if button is self.actions.button(QDialogButtonBox.Cancel):
            self.reject()
            return

        cpu_port = self.cpu_port_combo_box.currentText()
        gpu_port = self.gpu_port_combo_box.currentText()
        if cpu_port == gpu_port:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                "CPU and GPU COM ports cannot be the same",
            ).exec()
            return

        self.prefs.beginGroup("ports")
        self.prefs.setValue("cpu_port", cpu_port)
        self.prefs.setValue("gpu_port", gpu_port)
        self.prefs.endGroup()

        self.prefs.beginGroup("paths")
        self.prefs.setValue("jcap_path", self.jcap_path.text())
        self.prefs.endGroup()

        if button is self.actions.button(QDialogButtonBox.Ok):
            self.accept()
