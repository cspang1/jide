import re
import subprocess
import time
from serial import serial_for_url
from serial.tools import list_ports
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QLabel,
    QComboBox,
    QPushButton,
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
        self.cpu_port = None
        self.gpu_port = None

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
            self.cpu_port = self.prefs.value("cpu_port")
            self.cpu_port_combo_box.setCurrentText(self.cpu_port)
        if self.prefs.contains("gpu_port"):
            self.gpu_port = self.prefs.value("gpu_port")
            self.gpu_port_combo_box.setCurrentText(self.gpu_port)
        self.prefs.endGroup()
        self.cpu_port_combo_box.currentTextChanged.connect(self.setCpuPort)
        self.gpu_port_combo_box.currentTextChanged.connect(self.setGpuPort)

        auto_ident = QPushButton("Auto-Identify CPU/GPU")
        auto_ident.clicked.connect(self.idUcs)
        settings_form.addRow(QLabel("Propeller Ports"))
        settings_form.addRow("CPU Port:", self.cpu_port_combo_box)
        settings_form.addRow("GPU Port:", self.gpu_port_combo_box)
        settings_form.addRow(auto_ident)
        settings_form.addWidget(self.actions)
        self.setLayout(settings_form)

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

        if not new_cpu_port or not new_gpu_port:
            # Error dialog
            return

        self.setCpuPort(new_cpu_port)
        self.setGpuPort(new_gpu_port)

        self.cpu_port_combo_box.setCurrentText(self.cpu_port)
        self.gpu_port_combo_box.setCurrentText(self.gpu_port)

    def setCpuPort(self, port):
        """Sets the GPU COM port in preferences

        :param port: COM port hosting the CPU
        :type port: str
        """
        self.cpu_port = port

    def setGpuPort(self, port):
        """Sets the GPU COM port in preferences

        :param port: COM port hosting the GPU
        :type port: str
        """
        self.gpu_port = port

    def handlePrefsBtns(self, button):
        """Handles Ok/Apply/Cancel preferences buttons

        :param button: Button which triggered the actions
        :type button: QPushButton
        """
        if button is self.actions.button(QDialogButtonBox.Cancel):
            self.reject()
        self.prefs.beginGroup("ports")
        self.prefs.setValue("cpu_port", self.cpu_port)
        self.prefs.setValue("gpu_port", self.gpu_port)
        self.prefs.endGroup()
        if button is self.actions.button(QDialogButtonBox.Ok):
            self.accept()
