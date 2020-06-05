import pytest
import sys, os
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide


@pytest.fixture
def main_window(qtbot):
    print("start of session")
    widget = jide()
    qtbot.addWidget(widget)
    return widget
