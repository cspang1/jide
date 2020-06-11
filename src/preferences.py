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

        self.actions = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Cancel
        )
        self.actions.clicked.connect(self.handlePrefsBtns)
        settings_form = QFormLayout()

        self.cpu_port_combo_box = QComboBox()
        self.gpu_port_combo_box = QComboBox()
        self.prefs.beginGroup("ports")
        if self.prefs.contains("cpu_port"):
            self.cpu_port_combo_box.addItem(self.prefs.value("cpu_port"))
        if self.prefs.contains("gpu_port"):
            self.gpu_port_combo_box.addItem(self.prefs.value("gpu_port"))
        self.prefs.endGroup()

        auto_ident = QPushButton("Auto-Identify CPU/GPU")
        auto_ident.clicked.connect(self.idUcs)
        settings_form.addRow(QLabel("Propeller Ports"))
        settings_form.addRow("CPU Port:", self.cpu_port_combo_box)
        settings_form.addRow("GPU Port:", self.gpu_port_combo_box)
        settings_form.addRow(auto_ident)
        settings_form.addWidget(self.actions)
        self.setLayout(settings_form)

    def idUcs(self):
        cpu_port = None
        gpu_port = None
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
                timeout = 10
                while not response and time.time() < start + timeout:
                    ser.write(b"\x59")
                    response = ser.read(3)
                ser.close()
                if response == b"CPU":
                    cpu_port = port
                elif response == b"GPU":
                    gpu_port = port

        if not cpu_port or not gpu_port:
            # Error dialog
            return

        self.prefs.beginGroup("ports")
        self.prefs.setValue("cpu_port", cpu_port)
        self.prefs.setValue("gpu_port", gpu_port)
        self.prefs.endGroup()
        self.cpu_port_combo_box.addItem(cpu_port)
        self.gpu_port_combo_box.addItem(gpu_port)

    def handlePrefsBtns(self, button):
        if button is self.actions.button(QDialogButtonBox.Apply):
            print("Apply")
        elif button is self.actions.button(QDialogButtonBox.Ok):
            print("Applied and closed")
            self.accept()
        else:
            print("Cancelled")
            self.reject()
