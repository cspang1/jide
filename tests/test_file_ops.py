import sys, os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication


sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide
from source import Source


def test_file_open(qtbot):
    app = jide()
    qtbot.addWidget(app)

    dat_path = Path(__file__).parents[1] / "data" / "demo.jrf"
    app.loadProject(dat_path)

    assert app.windowTitle() == "JIDE - JCAP Demo"
