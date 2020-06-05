import pytest
import sys, os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide


@pytest.fixture
def main_window(qtbot):
    widget = jide()
    qtbot.addWidget(widget)
    return widget
