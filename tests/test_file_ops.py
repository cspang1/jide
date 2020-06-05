import sys, os

# from PyQt5.QtGui import QColor


sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide
from source import Source


def test_file_open(qtbot):
    print("start of test")
    temp = jide()
    qtbot.addWidget(temp)
    palettes = temp.data.getColPals(Source.SPRITE)
    for pal in palettes:
        for color in pal:
            print(color.rgb())
    assert True
